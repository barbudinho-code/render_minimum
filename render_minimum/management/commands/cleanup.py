"""
Django management command to perform database cleanup.

Removes:
- Expired, unconfirmed posts (older than cooldown window * 2).
- Expired confirmation tokens that were not consumed.
- Expired moderator tokens.

Usage:
    python manage.py cleanup   # Run all cleanup tasks
    python manage.py cleanup --dry-run  # Preview what would be deleted
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Cleanup expired data from the database."""

    help = "Remove expired unconfirmed posts and old tokens"

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )

    def handle(self, *args, **options):
        """Handle cleanup operations."""
        import time
        from render_minimum.models import (
            Post,
            ConfirmationToken,
            ModeratorToken,
        )
        from render_minimum import settings as django_settings
        from datetime import timedelta

        dry_run = options["dry_run"]

        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("Database Cleanup"))
        self.stdout.write("=" * 60)

        # Calculate cutoff times.
        now = int(time.time())

        # Expired unconfirmed posts (older than cooldown window * 2).
        post_cutoff = now - (django_settings.EMAIL_COOLDOWN_SECONDS * 2)
        expired_posts = Post.objects.filter(
            state=Post.AWAITING_CONFIRMATION,
            confirmed_at__isnull=True,
            created_at__lt=post_cutoff,
        )

        self.stdout.write(f"\nExpired unconfirmed posts (older than {django_settings.EMAIL_COOLDOWN_SECONDS * 2} seconds):")
        self.stdout.write(f"  Cutoff time: {post_cutoff}")
        self.stdout.write(f"  Count: {expired_posts.count()}")

        if not dry_run and expired_posts.exists():
            count = expired_posts.count()
            Post.objects.filter(
                state=Post.AWAITING_CONFIRMATION,
                confirmed_at__isnull=True,
                created_at__lt=post_cutoff,
            ).delete()
            self.stdout.write(self.style.SUCCESS(f"  Deleted {count} expired posts"))

        # Expired but not consumed confirmation tokens.
        expired_confirm_tokens = ConfirmationToken.objects.filter(
            expires_at__lt=now,
            consumed=False,
        )

        self.stdout.write(f"\nExpired but unconsumed confirmation tokens:")
        self.stdout.write(f"  Count: {expired_confirm_tokens.count()}")

        if not dry_run and expired_confirm_tokens.exists():
            count = expired_confirm_tokens.count()
            expired_confirm_tokens.delete()
            self.stdout.write(self.style.SUCCESS(f"  Deleted {count} expired tokens"))

        # Expired moderator tokens.
        expired_moderator_tokens = ModeratorToken.objects.filter(
            expires_at__lt=now,
        )

        self.stdout.write(f"\nExpired moderator tokens:")
        self.stdout.write(f"  Count: {expired_moderator_tokens.count()}")

        if not dry_run and expired_moderator_tokens.exists():
            count = expired_moderator_tokens.count()
            expired_moderator_tokens.delete()
            self.stdout.write(self.style.SUCCESS(f"  Deleted {count} expired tokens"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("Cleanup complete"))
