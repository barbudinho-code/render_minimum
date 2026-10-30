"""
Django management command to run the task worker.

This script processes:
- Email queue items (send confirmation/rejection/moderation emails).
- AI classification tasks.
- Database cleanup of expired unconfirmed posts.

Usage:
    python manage.py worker               # Start worker in foreground
    celery -A render_minimum worker -l INFO  # Alternative with Celery (optional)
"""

from datetime import timedelta
import os
import sys


from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Task worker for processing email and AI tasks.

    This command processes the database-backed task queue:
    1. Claims pending email tasks atomically.
    2. Sends emails via SMTP (or console backend in development).
    3. Marks tasks as sent or failed after retry attempts are exhausted.
    4. Deletes expired unconfirmed posts during periodic cleanup.

    The worker uses the EmailTaskQueue and TaskLog models to track progress.

    Run in production:
        python manage.py worker           # Background process (no Celery)
    """

    help = "Process email and AI tasks from the database queue"

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            "--queue-timeout",
            type=int,
            default=300,
            help="Seconds to wait between claiming tasks (default: 300)",
        )
        parser.add_argument(
            "--max-claims",
            type=int,
            default=None,
            help="Maximum number of claims per run (None = unlimited)",
        )

    def handle(self, *args, **options):
        """Handle command execution."""
        from django.conf import settings
        from render_minimum.models import (
            EmailTaskQueue,
            TaskLog,
            Post,
            ConfirmationToken,
            ModeratorToken,
        )

        queue_timeout = options["queue_timeout"]
        max_claims = options["max_claims"]

        # Log header.
        self.stdout.write(self.style.SUCCESS("Starting worker..."))
        self.stdout.write(f"Queue timeout: {queue_timeout} seconds")
        self.stdout.write(f"Max claims per run: {max_claims or 'unlimited'}")
        self.stdout.write("")

        claim_count = 0

        try:
            # Main loop - continuously process tasks.
            while True:
                # Wait before trying to claim the next task.
                import time
                time.sleep(queue_timeout)

                # Break if max claims reached.
                if max_claims and claim_count >= max_claims:
                    self.stdout.write(f"Max claims ({max_claims}) reached, shutting down.")
                    break

                # Claim a pending email task atomically using select_for_update.
                with self.db.connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, post_id, recipient_email, subject, body, created_at, next_retry_at, attempt_count
                        FROM render_minimum_emailtaskqueue
                        WHERE status IN (%s, %s)
                          AND (next_retry_at IS NULL OR next_retry_at < %s)
                          AND id = (
                              SELECT MIN(id)
                              FROM render_minimum_emailtaskqueue
                              WHERE status IN (%s, %s)
                                AND (next_retry_at IS NULL OR next_retry_at < %s)
                          )
                        FOR UPDATE;
                        """,
                        [
                            EmailTaskQueue.STATUS_PENDING,
                            EmailTaskQueue.STATUS_CLAIMED,
                            settings.CONFIRMATION_DEADLINE_SECONDS,
                            EmailTaskQueue.STATUS_PENDING,
                            EmailTaskQueue.STATUS_CLAIMED,
                            settings.CONFIRMATION_DEADLINE_SECONDS,
                        ],
                    )

                if not cursor.fetchone():
                    # No tasks to claim. Wait longer next time.
                    self.stdout.write("No pending tasks available. Waiting...")
                    continue

                # Fetch the task row using Django ORM (outside transaction).
                task = EmailTaskQueue.objects.select_for_update(of=["*"]).only(
                    "id",
                    "post_id",
                    "recipient_email",
                    "subject",
                    "body",
                    "next_retry_at",
                    "attempt_count",
                ).first()

                if not task:
                    continue

                # Mark as claimed.
                task.status = EmailTaskQueue.STATUS_CLAIMED
                task.claimed_at = int(time.time())
                task.save(update_fields=["status", "claimed_at"])

                self.stdout.write(
                    self.style.SUCCESS(f"Processing email task #{task.id} for post #{task.post_id} to {task.recipient_email}")
                )

                claim_count += 1

                # Attempt to send the email.
                success = self.send_email(task)

                if success:
                    # Mark as sent and clear retry timestamp.
                    task.status = EmailTaskQueue.STATUS_SENT
                    task.next_retry_at = None
                    task.save(update_fields=["status", "next_retry_at"])
                    self.stdout.write(self.style.SUCCESS("Email sent successfully"))
                else:
                    # Mark as failed with reason (without secrets).
                    log_entry = TaskLog(
                        task_type="email",
                        status="failure",
                        details=(
                            f"Post #{task.post_id}: Failed to send email. "
                            f"Attempt {task.attempt_count}. Reason: SMTP or delivery error."
                        ),
                    )
                    log_entry.save()

                    # Retry if within max attempts.
                    if task.attempt_count < settings.TASK_MAX_ATTEMPTS:
                        self.stdout.write("Retrying email...")
                        task.retry()
                    else:
                        self.stdout.write(self.style.WARNING(f"Max retries reached for post #{task.post_id}"))

                # Perform periodic cleanup - delete expired unconfirmed posts.
                self.cleanup_expired_posts()

        except KeyboardInterrupt:
            self.stdout.write("")
            self.stdout.write("Worker shutting down...")

    def send_email(self, task) -> bool:
        """
        Send an email for a queued task.

        Returns True if successful, False otherwise.
        """
        from django.core.mail import EmailMessage

        try:
            # Build the HTML content.
            html_content = task.body.strip()

            # Replace any newlines with <br> for display.
            html_content = html_content.replace("\n", "<br>")

            email_message = EmailMessage(
                subject=task.subject,
                body=html_content,
                to=[task.recipient_email],
                from_email=os.getenv("DEFAULT_FROM_EMAIL", "noreply@local"),
            )

            # Send the email.
            email_message.send(fail_silently=False)

            return True

        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Failed to send email: {exc}"))
            return False

    def cleanup_expired_posts(self):
        """
        Delete expired, unconfirmed posts.

        This is called periodically during task processing.
        Posts that have been confirmed cannot be deleted by this command.
        """
        from datetime import timedelta
        from render_minimum.models import Post, CooldownRecord

        cutoff_time = int(time.time()) - (settings.EMAIL_COOLDOWN_SECONDS * 2)

        expired_posts = (
            Post.objects.filter(state=Post.AWAITING_CONFIRMATION, created_at__lt=cutoff_time)
            .exclude(confirmed_at__isnull=False)
        )

        if expired_posts.exists():
            # Delete only unconfirmed posts older than the cooldown window.
            count = expired_posts.count()
            Post.objects.filter(
                state=Post.AWAITING_CONFIRMATION,
                created_at__lt=cutoff_time,
            ).delete()
            self.stdout.write(self.style.WARNING(f"Cleaned up {count} expired unconfirmed posts"))

    def cleanup_expired_tokens(self):
        """Delete expired confirmation and moderator tokens."""
        from render_minimum.models import ConfirmationToken, ModeratorToken

        now = int(time.time())

        # Delete expired but not consumed tokens.
        ConfirmationToken.objects.filter(expires_at__lt=now, consumed=False).delete()
        ModeratorToken.objects.filter(expires_at__lt=now).delete()


def main():
    """Run the worker in a long-running process."""
    import django

    # Initialize Django settings.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "render_minimum.settings")
    django.setup()

    from django.core.management import execute_from_command_line
    sys.argv = ["manage.py", "worker"]
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
