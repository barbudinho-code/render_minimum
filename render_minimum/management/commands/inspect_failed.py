"""
Django management command to inspect failed task queue items.

Usage:
    python manage.py inspect-failed   # List failed tasks
    python manage.py inspect-failed --format json  # JSON output
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Inspect failed tasks in the queue."""

    help = "Display failed email and AI tasks"

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            "--format",
            choices=["text", "json"],
            default="text",
            help="Output format (default: text)",
        )

    def handle(self, *args, **options):
        """Handle failed task inspection."""
        from render_minimum.models import EmailTaskQueue, Post, TaskLog

        # Get failed tasks.
        failed_tasks = EmailTaskQueue.objects.filter(status="failed")

        if options["format"] == "json":
            import json
            data = []
            for task in failed_tasks:
                post = Post.objects.get(pk=task.post_id) if task.post_id else None
                data.append({
                    "id": task.id,
                    "post_id": task.post_id,
                    "recipient_email": task.recipient_email,
                    "subject": task.subject[:50],
                    "attempt_count": task.attempt_count,
                    "created_at": task.created_at,
                })
            self.stdout.write(json.dumps(data, indent=2))
        else:
            self.stdout.write(self.style.WARNING("Failed Tasks"))
            self.stdout.write("-" * 60)

            for task in failed_tasks[:10]:  # Limit to first 10 for readability.
                post = Post.objects.get(pk=task.post_id) if task.post_id else None
                self.stdout.write(f"\nTask #{task.id}")
                self.stdout.write(f"  Post ID: {task.post_id or 'N/A'}")
                self.stdout.write(f"  Recipient: {task.recipient_email}")
                self.stdout.write(f"  Subject: {task.subject[:60]}...")
                self.stdout.write(f"  Attempts: {task.attempt_count}")
                self.stdout.write(f"  Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

            if len(failed_tasks) > 10:
                self.stdout.write(
                    f"\n...\n\nShowing first {len(failed_tasks)} failed tasks. "
                    f"Use the database directly for more details."
                )
