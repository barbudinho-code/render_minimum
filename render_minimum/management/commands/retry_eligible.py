"""
Django management command to retry eligible failed tasks.

Usage:
    python manage.py retry-eligible  # Retry all eligible failed tasks
    python manage.py retry-eligible --count 5  # Retry up to 5 tasks
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Retry eligible failed email tasks."""

    help = "Retry failed tasks that are within the maximum attempt count"

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            "--count",
            type=int,
            default=None,
            help="Maximum number of tasks to retry (None = all)",
        )

    def handle(self, *args, **options):
        """Handle eligible task retry."""
        from render_minimum.models import EmailTaskQueue

        count = options["count"]
        max_count = count or None

        # Get failed tasks that are eligible for retry (attempt count < TASK_MAX_ATTEMPTS).
        from render_minimum import settings as django_settings
        eligible_tasks = EmailTaskQueue.objects.filter(
            status="failed",
            attempt_count__lt=django_settings.TASK_MAX_ATTEMPTS,
        )

        total_retried = 0

        if not eligible_tasks.exists():
            self.stdout.write(self.style.SUCCESS("No failed tasks found"))
            return

        if max_count:
            eligible_tasks = eligible_tasks[:max_count]
            self.stdout.write(f"Will retry up to {max_count} tasks")

        for task in eligible_tasks:
            # Reset the task status.
            task.status = EmailTaskQueue.STATUS_PENDING
            task.next_retry_at = None
            task.save(update_fields=["status", "next_retry_at"])
            self.stdout.write(self.style.SUCCESS(f"Retried task #{task.id} for post #{task.post_id}"))
            total_retried += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"{total_retried} tasks retried"))
