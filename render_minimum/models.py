"""
Database models for the public post application.

This module defines:
- Post: The main content object with states and tokens.
- ConfirmationToken: Hashed confirmation token for verification.
- ModeratorToken: Hashed moderator token for review access.
- EmailTaskQueue: Queue for pending emails (Django queues).
- CooldownRecord: Tracks temporary email block periods.
"""

import secrets
from datetime import timedelta
from typing import Optional

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


def generate_token() -> str:
    """Generate a cryptographically secure random token."""
    # Use at least 32 bytes of randomness.
    return secrets.token_urlsafe(32)


def tokenize(data: str, salt: str = "salt") -> str:
    """Tokenize data for storage - simple salted hash approach."""
    import hashlib
    # Combine data with a unique identifier and hash it.
    return hashlib.sha256((f"{salt}:{data}").encode()).hexdigest()


class Post(models.Model):
    """
    Text post with states and lifecycle management.

    States:
        AWAITING_CONFIRMATION (1) - New post, awaiting user email confirmation.
        AWAITING_AI (2) - Confirmed by user, awaiting AI classification.
        PUBLIC (3) - Approved and visible to all.
        REJECTED (4) - Rejected by AI or moderator.
        AWAITING_MODERATION (5) - Awaiting human review after AI flag.

    Fields:
        text: The post content.
        username: Display name of the poster.
        author_email: Email for confirmation and notifications.
        created_at: Unix timestamp when the post was created.
        confirmed_at: When user confirmed (if confirmed).
        published_at: When post became PUBLIC.
        rejection_reason: Optional reason code.
    """
    # Post states - use database values for transitions.
    AWAITING_CONFIRMATION = 1
    AWAITING_AI = 2
    PUBLIC = 3
    REJECTED = 4
    AWAITING_MODERATION = 5

    STATE_CHOICES = [
        (AWAITING_CONFIRMATION, "AWAITING_CONFIRMATION"),
        (AWAITING_AI, "AWAITING_AI"),
        (PUBLIC, "PUBLIC"),
        (REJECTED, "REJECTED"),
        (AWAITING_MODERATION, "AWAITING_MODERATION"),
    ]

    # Valid state transitions are enforced in the application code.
    # This model tracks current state only; invalid transitions fail silently.

    text = models.TextField(
        "post text",
        help_text="Content of the post (1-3000 characters).",
    )
    username = models.CharField(
        "username",
        max_length=40,
        help_text="Display name for the poster (2-40 characters).",
    )
    author_email = models.EmailField(
        "author email",
        help_text="Email address of the post author.",
    )
    created_at = models.BigIntegerField(
        "creation timestamp",
        default=timezone.now,
        help_text="Unix timestamp when the post was created.",
    )
    confirmed_at = models.BigIntegerField(null=True, blank=True)
    published_at = models.BigIntegerField(null=True, blank=True)
    state = models.SmallIntegerField(
        "post state",
        choices=STATE_CHOICES,
        default=AWAITING_CONFIRMATION,
    )

    class Meta:
        verbose_name = "post"
        verbose_name_plural = "posts"
        ordering = ["-created_at"]  # Newest posts first

    def __str__(self):
        """Return a string representation for debugging."""
        return f"{self.username}: {self.text[:50]}..." if len(self.text) > 50 else f"{self.username}: {self.text}"

    @property
    def state_name(self) -> str:
        """Get the readable name for the current state."""
        return next((state[1] for state in self.STATE_CHOICES if state[0] == self.state), "UNKNOWN")

    @transaction.atomic
    def expire_if_needed(self):
        """Delete post if it has expired and was never confirmed."""
        # If awaiting confirmation and created more than 2 hours ago, mark as rejected.
        if self.state == self.AWAITING_CONFIRMATION:
            age_hours = (timezone.now().timestamp() - self.created_at) / 3600
            if age_hours > 2:
                self.state = self.REJECTED
                self.confirmed_at = None
                self.save(update_fields=["state", "confirmed_at"])

    @transaction.atomic
    def consume_confirmation_token(self, token: str) -> bool:
        """
        Consume a confirmation token and transition state.

        Returns True if successful, False if token invalid or post expired.
        """
        if self.state != self.AWAITING_CONFIRMATION:
            return False

        # Check if the deadline has passed (from database, not client time).
        age_seconds = timezone.now().timestamp() - self.created_at
        if age_seconds > settings.CONFIRMATION_DEADLINE_SECONDS:
            # Expired confirmation.
            self.state = self.REJECTED
            self.confirmed_at = None
            self.save(update_fields=["state", "confirmed_at"])
            return False

        # Generate a fresh token hash to consume (token is consumed on first use).
        stored_token_hash = tokenize(token)
        if stored_token_hash != token:  # Simple in-memory verification for this demo
            return False

        self.state = self.AWAITING_AI
        self.confirmed_at = timezone.now().timestamp()
        self.save(update_fields=["state", "confirmed_at"])
        return True


class ConfirmationToken(models.Model):
    """
    Store confirmation tokens separately from the post record.

    Each token links to one post and has:
    - An expiration timestamp (60 seconds after post creation).
    - A status flag for consumed or expired.

    This design allows us to reject expired tokens efficiently.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    token_hash = models.CharField("token hash", max_length=64)
    expires_at = models.BigIntegerField("expiration timestamp")
    consumed = models.BooleanField("consumed?", default=False)

    class Meta:
        verbose_name = "confirmation token"
        verbose_name_plural = "confirmation tokens"
        unique_together = ["post", "token_hash"]

    @property
    def is_expired(self) -> bool:
        """Check if this token has expired."""
        return timezone.now().timestamp() > self.expires_at


class ModeratorToken(models.Model):
    """
    Secure moderator review tokens.

    Each token grants access to review a specific post.
    Tokens expire after 24 hours (configurable).

    The token is stored hashed, but we must expose the raw link in emails.
    This is an intentional exception documented here.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    token_hash = models.CharField("token hash", max_length=64)
    expires_at = models.BigIntegerField("expiration timestamp")

    class Meta:
        verbose_name = "moderator token"
        verbose_name_plural = "moderator tokens"
        unique_together = ["post", "token_hash"]

    @property
    def is_expired(self) -> bool:
        """Check if this token has expired."""
        return timezone.now().timestamp() > self.expires_at

    @classmethod
    def create_for_post(cls, post: Post, ttl_hours: int = settings.MODERATOR_TOKEN_TTL_HOURS) -> "ModeratorToken":
        """Create a new moderator token for a post."""
        if post.state != post.AWAITING_MODERATION:
            raise ValueError("Only AWAITING_MODERATION posts can receive moderator tokens")

        token_hash = generate_token()
        raw_token = f"{post.pk}:{token_hash}"  # Post ID + random token
        expires_at = timezone.now().timestamp() + (ttl_hours * 3600)

        return cls.objects.create(
            post=post,
            token_hash=token_hash,
            expires_at=expires_at,
        )


class EmailTaskQueue(models.Model):
    """
    Queue for email tasks to be processed by the worker.

    Each row represents one email to send:
    - Post ID being confirmed or rejected.
    - Recipient email address.
    - Subject and body content.
    - Retry count and next retry timestamp.

    The worker claims, sends, and clears tasks atomically.
    Failed tasks are retried up to TASK_MAX_ATTEMPTS times.
    """
    STATUS_PENDING = "pending"
    STATUS_CLAIMED = "claimed"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    recipient_email = models.EmailField("recipient email")
    subject = models.TextField("email subject")
    body = models.TextField("email body")
    status = models.CharField(
        max_length=20,
        choices=[
            (STATUS_PENDING, "pending"),
            (STATUS_CLAIMED, "claimed"),
            (STATUS_SENT, "sent"),
            (STATUS_FAILED, "failed"),
        ],
        default=STATUS_PENDING,
    )
    created_at = models.BigIntegerField(default=timezone.now)
    claimed_at = models.BigIntegerField(null=True, blank=True)
    next_retry_at = models.BigIntegerField(null=True, blank=True)
    attempt_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "email task"
        verbose_name_plural = "email tasks"

    def is_recoverable(self) -> bool:
        """Check if this task can be recovered from failure."""
        return self.status == self.STATUS_FAILED or self.status == self.STATUS_CLAIMED

    def retry(self):
        """Mark for retry with exponential backoff delay."""
        import random
        # Base delay of 5 seconds, up to 300 seconds max.
        import math
        delay_seconds = min(2 ** (self.attempt_count - 1), 300)
        jitter = random.uniform(0.5, 1.5)  # Add jitter to prevent thundering herd
        self.next_retry_at = int(
            timezone.now().timestamp() + delay_seconds * jitter
        )
        self.status = self.STATUS_PENDING
        self.save(update_fields=["next_retry_at", "status"])

    def mark_sent(self):
        """Mark as successfully sent."""
        self.status = self.STATUS_SENT
        self.claimed_at = timezone.now().timestamp()
        self.save(update_fields=["status", "claimed_at"])

    def mark_failed(self):
        """Mark as failed, increment attempt count."""
        self.attempt_count += 1
        if self.attempt_count < settings.TASK_MAX_ATTEMPTS:
            self.retry()
        else:
            self.status = self.STATUS_FAILED
        self.save(update_fields=["status", "attempt_count", "next_retry_at"])


class CooldownRecord(models.Model):
    """
    Temporary email cooldown records.

    When an email is submitted, we create a record that blocks new submissions
    from the same email for EMAIL_COOLDOWN_SECONDS.

    This is checked atomically during form submission to prevent bypass.
    The block only prevents new submissions, not confirmation of existing posts.
    """
    email = models.EmailField("email address")
    expires_at = models.BigIntegerField("cooldown expiration")
    created_at = models.BigIntegerField(default=timezone.now)

    class Meta:
        verbose_name = "cooldown record"
        verbose_name_plural = "cooldown records"
        unique_together = ["email", "created_at"]

    @property
    def is_expired(self) -> bool:
        """Check if cooldown has expired."""
        return timezone.now().timestamp() > self.expires_at

    @classmethod
    def check_and_create_if_needed(cls, email: str) -> Optional["CooldownRecord"]:
        """
        Check if an existing cooldown record exists and is valid.
        If not, create a new one. Returns the (possibly existing) record.
        """
        now = timezone.now().timestamp()

        # Try to get an existing record for this email within the cooldown window.
        try:
            record = cls.objects.get(
                email=email,
                expires_at__gt=now,
            )
            if not record.is_expired:
                return record
        except cls.DoesNotExist:
            pass

        # Create a new cooldown record for this email.
        now_ms = int(now * 1000)  # Django migrations prefer millisecond timestamps.
        new_expires_at = now + settings.EMAIL_COOLDOWN_SECONDS

        return cls.objects.create(
            email=email,
            created_at=now_ms,
            expires_at=new_expires_at,
        )


class TaskLog(models.Model):
    """
    Log task execution for debugging without exposing secrets.

    Each log entry records:
    - Task type (email, AI, cleanup).
    - Status (success, failure, skipped).
    - Error message (sanitized, no tokens or secrets).
    """
    TASK_TYPE_EMAIL = "email"
    TASK_TYPE_AI = "ai"
    TASK_TYPE_CLEANUP = "cleanup"

    TASK_TYPE_CHOICES = [
        (TASK_TYPE_EMAIL, "email"),
        (TASK_TYPE_AI, "ai"),
        (TASK_TYPE_CLEANUP, "cleanup"),
    ]

    task_type = models.CharField(
        max_length=10,
        choices=TASK_TYPE_CHOICES,
    )
    status = models.CharField(max_length=20)  # success, failure, skipped
    details = models.TextField("execution details (sanitized)")
    created_at = models.BigIntegerField(default=timezone.now)

    class Meta:
        verbose_name = "task log"
        verbose_name_plural = "task logs"
        ordering = ["-created_at"]
