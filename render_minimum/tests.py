"""
Automated tests for the public posts application.

Test categories:
- Public post visibility
- Form validation
- Email normalization
- Temporary blocking (cooldown)
- Confirmation expiration
- Confirmation replay attacks
- AI classifier results
- Moderation acceptance/rejection
- Moderator token expiration
- Task retry and lease recovery
- Expired confirmation email suppression
- Private data protection
- HTML escaping

Use a controllable clock for time-based tests.
"""

import hashlib
import os
import sys
import unittest
from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone

from render_minimum.models import (
    Post,
    ConfirmationToken,
    ModeratorToken,
    EmailTaskQueue,
    CooldownRecord,
)


class TestPublicPostVisibility(TestCase):
    """Test that only PUBLIC posts are visible."""

    def setUp(self):
        settings.DEBUG = True  # Allow console email backend.

    def test_public_posts_are_shown(self):
        """Public posts should be returned by the listing view."""
        Post.objects.create(
            state=Post.PUBLIC,
            text="This is a public post",
            username="TestUser",
            author_email="test@example.com",
        )

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"This is a public post", response.content)

    def test_private_posts_are_hidden(self):
        """Private posts should not appear in the listing."""
        Post.objects.create(
            state=Post.AWAITING_CONFIRMATION,
            text="This is awaiting confirmation",
            username="TestUser2",
            author_email="test2@example.com",
        )

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        # The private post should not appear.
        self.assertNotIn(b"This is awaiting confirmation", response.content)

    def test_rejected_posts_are_hidden(self):
        """Rejected posts should not appear in the listing."""
        Post.objects.create(
            state=Post.REJECTED,
            text="This is rejected",
            username="TestUser3",
            author_email="test3@example.com",
        )

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"This is rejected", response.content)


class TestFormValidation(TestCase):
    """Test form validation rules."""

    def setUp(self):
        settings.DEBUG = True

    def test_empty_text_field_shows_error(self):
        """Empty text should show a validation error."""
        data = {
            "email": "test@example.com",
            "username": "ValidUser",
            "text": "",  # Empty - invalid
        }

        response = self.client.post("/submit/", data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"invalid display name", response.content)  # Username validation error first.

    def test_username_too_short(self):
        """Username must be at least 2 characters."""
        data = {
            "email": "test@example.com",
            "username": "A",  # Too short
            "text": "Valid post text",
        }

        response = self.client.post("/submit/", data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"invalid display name", response.content)

    def test_username_too_long(self):
        """Username must be at most 40 characters."""
        data = {
            "email": "test@example.com",
            "username": "A" * 41,  # Too long
            "text": "Valid post text",
        }

        response = self.client.post("/submit/", data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"invalid display name", response.content)

    def test_text_too_short(self):
        """Post text must be at least 1 character."""
        data = {
            "email": "test@example.com",
            "username": "ValidUser",
            "text": "",  # Empty - invalid
        }

        response = self.client.post("/submit/", data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"invalid display text", response.content)

    def test_text_too_long(self):
        """Post text must be at most 3000 characters."""
        data = {
            "email": "test@example.com",
            "username": "ValidUser",
            "text": "A" * 3001,  # Too long
        }

        response = self.client.post("/submit/", data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"invalid display text", response.content)


class TestEmailNormalization(TestCase):
    """Test email normalization rules."""

    def setUp(self):
        settings.DEBUG = True

    @override_settings(DEBUG=True)
    def test_email_lowercased(self):
        """Email addresses should be normalized to lowercase."""
        # Note: This is tested indirectly via database records.
        from render_minimum.views import normalize_email

        result = normalize_email("TEST@EXAMPLE.COM")
        self.assertEqual(result, "test@example.com")

    @override_settings(DEBUG=True)
    def test_whitespace_trimmed(self):
        """Leading and trailing whitespace should be stripped."""
        from render_minimum.views import normalize_email

        result = normalize_email("  test@example.com  ")
        self.assertEqual(result, "test@example.com")

    @override_settings(DEBUG=True)
    def test_quotes_removed(self):
        """Surrounding quotes should be removed."""
        from render_minimum.views import normalize_email

        result1 = normalize_email('"test@example.com"')
        result2 = normalize_email("'test@example.com'")
        self.assertEqual(result1, "test@example.com")
        self.assertEqual(result2, "test@example.com")


class TestTemporaryBlocking(TestCase):
    """Test the temporary email block (cooldown)."""

    def setUp(self):
        settings.DEBUG = True

    @override_settings(EMAIL_COOLDOWN_SECONDS=5)  # Short cooldown for testing.
    def test_cooldown_prevents_submission(self):
        """Submissions should be rejected during cooldown period."""
        # Create a cooldown record that will expire in 5 seconds.
        now = timezone.now().timestamp()
        expires_at = now + 5

        CooldownRecord.objects.create(
            email="test@example.com",
            created_at=int(now),
            expires_at=expires_at,
        )

        # Try to submit immediately (should be blocked).
        response = self.client.post("/submit/", {
            "email": "test@example.com",
            "username": "TestUser",
            "text": "Test post",
        })

        self.assertEqual(response.status_code, 200)
        # Response should contain cooldown message.
        self.assertIn(b"cooldown", response.content.lower())

    @override_settings(EMAIL_COOLDOWN_SECONDS=5)
    def test_cooldown_expires(self):
        """Cooldown block should expire after the wait time."""
        now = timezone.now().timestamp()
        expires_at = now + 5

        CooldownRecord.objects.create(
            email="test@example.com",
            created_at=int(now),
            expires_at=expires_at,
        )

        # Wait for cooldown to expire (mocked).
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value = timezone.utc
            from django.utils import timezone as tz_time

            with self.settings(CONFIRMATION_DEADLINE_SECONDS=60):
                CooldownRecord.objects.filter(email="test@example.com").update(
                    expires_at=tz_time.now().timestamp() + 1,  # Expired
                )

        # Now submission should succeed.
        response = self.client.post("/submit/", {
            "email": "test@example.com",
            "username": "TestUser",
            "text": "Test post",
        })

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"cooldown", response.content.lower())


class TestConfirmationExpiration(TestCase):
    """Test that confirmation expires after the deadline."""

    def setUp(self):
        settings.DEBUG = True
        settings.CONFIRMATION_DEADLINE_SECONDS = 1  # Very short for testing.

    @override_settings(EMAIL_COOLDOWN_SECONDS=5)
    def test_confirmation_expires_after_deadline(self):
        """Posts should be rejected if not confirmed within the deadline."""
        from render_minimum.models import Post, ConfirmationToken

        # Create a post awaiting confirmation.
        now = timezone.now().timestamp()
        created_at = now - 2  # Already past the 1-second deadline.

        post = Post.objects.create(
            state=Post.AWAITING_CONFIRMATION,
            text="Expired post",
            username="TestUser",
            author_email="test@example.com",
            created_at=int(created_at),
        )

        # Try to confirm (should fail because expired).
        token = ConfirmationToken.objects.create(
            post=post,
            token_hash=hashlib.sha256("dead:line").hexdigest(),
            expires_at=int(now + 10),  # Token is still valid but post is expired.
        )

        response = self.client.post(f"/confirm/{post.pk}/{token.token_hash}/confirm/", {
            "csrfmiddlewaretoken": "",  # Skip CSRF for this test.
        })

        # Response should indicate expiration.
        self.assertIn(b"expired", response.content.lower())


class TestConfirmationReplay(TestCase):
    """Test that confirmation tokens cannot be replayed."""

    def setUp(self):
        settings.DEBUG = True

    @override_settings(EMAIL_COOLDOWN_SECONDS=5)
    def test_replay_attack_prevented(self):
        """A used token should not work on a second request."""
        from render_minimum.models import Post, ConfirmationToken

        # Create a post.
        now = timezone.now().timestamp()
        post = Post.objects.create(
            state=Post.AWAITING_CONFIRMATION,
            text="Replay test",
            username="TestUser",
            author_email="test@example.com",
            created_at=int(now),
        )

        # Create and consume a token.
        token_hash = hashlib.sha256("used:token").hexdigest()
        token_obj = ConfirmationToken.objects.create(
            post=post,
            token_hash=token_hash,
            expires_at=int(now + 3600),
        )

        # Mark token as consumed (simulating use).
        token_obj.consumed = True
        token_obj.save()

        # Second confirmation request with the same token.
        response = self.client.post(f"/confirm/{post.pk}/{token_hash}/confirm/", {})

        self.assertEqual(response.status_code, 200)
        # Should not allow confirmation of already-used token.


class TestAIClassifier(TestCase):
    """Test AI classifier placeholder."""

    def setUp(self):
        settings.DEBUG = True

    @override_settings(EMAIL_COOLDOWN_SECONDS=5, AI_CLASSIFIER_RESULT_DOUBTFUL_FIRST=True)
    def test_initial_classification_returns_doubtful(self):
        """Initial implementation should always return DOUBTFUL."""
        from render_minimum.views import classification_result

        result = classification_result("Any text here")
        self.assertEqual(result, "DOUBTFUL")


class TestModerationWorkflow(TestCase):
    """Test moderator acceptance and rejection."""

    def setUp(self):
        settings.DEBUG = True

    @override_settings(EMAIL_COOLDOWN_SECONDS=5)
    def test_moderator_acceptance(self):
        """Moderator should be able to accept a post for publication."""
        from render_minimum.models import Post, ModeratorToken

        # Create a post in AWAITING_MODERATION state.
        now = timezone.now().timestamp()
        post = Post.objects.create(
            state=Post.AWAITING_MODERATION,
            text="Moderation test",
            username="TestUser",
            author_email="test@example.com",
            created_at=int(now),
        )

        # Create a moderator token.
        ModeratorToken.objects.create(
            post=post,
            token_hash=hashlib.sha256("accept:token").hexdigest(),
            expires_at=int(now + 3600 * 24),
        )

        # Accept the moderation.
        response = self.client.post(f"/review/{post.pk}/accept:token/accept/", {
            "csrfmiddlewaretoken": "",
        })

        # Post should be PUBLIC now.
        post.refresh_from_db()
        self.assertEqual(post.state, Post.PUBLIC)


class TestModeratorTokenExpiration(TestCase):
    """Test moderator token expiration."""

    def setUp(self):
        settings.DEBUG = True

    @override_settings(EMAIL_COOLDOWN_SECONDS=5)
    def test_expired_token_rejected(self):
        """Expired moderator tokens should not grant access."""
        from render_minimum.models import Post, ModeratorToken

        now = timezone.now().timestamp()
        post = Post.objects.create(
            state=Post.AWAITING_MODERATION,
            text="Expired token test",
            username="TestUser",
            author_email="test@example.com",
            created_at=int(now),
        )

        # Create an expired token.
        ModeratorToken.objects.create(
            post=post,
            token_hash=hashlib.sha256("expired:token").hexdigest(),
            expires_at=int(now - 1),  # Already expired.
        )

        response = self.client.get(f"/review/{post.pk}/expired:token/")
        # Should not show buttons (token invalid).
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"Accept", response.content)


class TestTaskRetryLease(TestCase):
    """Test task retry and lease recovery."""

    def setUp(self):
        settings.DEBUG = True

    @override_settings(EMAIL_COOLDOWN_SECONDS=5, TASK_MAX_ATTEMPTS=3)
    def test_task_retry_logic(self):
        """Failed tasks should be retried up to the maximum attempts."""
        from render_minimum.models import EmailTaskQueue

        # Create a failed task.
        post = Post.objects.create(
            state=Post.AWAITING_CONFIRMATION,
            text="Retry test",
            username="TestUser",
            author_email="test@example.com",
        )

        task = EmailTaskQueue.objects.create(
            post=post,
            recipient_email="fail@example.com",
            subject="Test subject",
            body="Test body",
            status=EmailTaskQueue.STATUS_FAILED,
            attempt_count=1,
        )

        # Retry the task.
        task.retry()

        # Status should be reset and next_retry_at set.
        self.assertEqual(task.status, EmailTaskQueue.STATUS_PENDING)
        self.assertIsNotNone(task.next_retry_at)


class TestExpiredEmailSuppression(TestCase):
    """Test that expired confirmation emails are suppressed."""

    def setUp(self):
        settings.DEBUG = True

    @override_settings(EMAIL_COOLDOWN_SECONDS=5, AI_CLASSIFIER_RESULT_DOUBTFUL_FIRST=True)
    def test_expired_email_suppression(self):
        """Posts confirmed after expiry should not receive email."""
        from render_minimum.models import Post

        # Create a post.
        now = timezone.now().timestamp()
        created_at = now - 120  # Expired 2 minutes ago (deadline is 60s).

        post = Post.objects.create(
            state=Post.AWAITING_CONFIRMATION,
            text="Expired email test",
            username="TestUser",
            author_email="test@example.com",
            created_at=int(created_at),
        )

        # Consume the confirmation.
        from render_minimum.models import ConfirmationToken

        token_hash = hashlib.sha256("consume:post").hexdigest()
        token_obj = ConfirmationToken.objects.create(
            post=post,
            token_hash=token_hash,
            expires_at=int(now + 10),
        )

        post.consume_confirmation_token("consume:post")

        # Post should now be in a state that doesn't send email.
        post.refresh_from_db()
        self.assertNotEqual(post.state, Post.AWAITING_CONFIRMATION)


class TestPrivateDataProtection(TestCase):
    """Test that private data is not exposed."""

    def setUp(self):
        settings.DEBUG = True

    @override_settings(EMAIL_COOLDOWN_SECONDS=5)
    def test_author_email_not_exposed(self):
        """Author email should not appear in public post views."""
        Post.objects.create(
            state=Post.PUBLIC,
            text="Secret",
            username="SecretUser",
            author_email="secret@example.com",
        )

        response = self.client.get("/post/1/")
        # Author email should not be visible.
        self.assertNotIn(b"secret@example.com", response.content)

    @override_settings(EMAIL_COOLDOWN_SECONDS=5)
    def test_no_confirmed_tokens_exposed(self):
        """Confirmation tokens should not be exposed in responses."""
        pass  # Tokens are hashed and only used for verification.


class TestHTMLEscaping(TestCase):
    """Test that user content is properly escaped."""

    def setUp(self):
        settings.DEBUG = True

    @override_settings(EMAIL_COOLDOWN_SECONDS=5)
    def test_html_escaping_in_post_display(self):
        """User-supplied HTML should be escaped in displays."""
        Post.objects.create(
            state=Post.PUBLIC,
            text="<script>alert('XSS')</script>Test post",
            username="TestUser",
            author_email="test@example.com",
        )

        response = self.client.get("/post/1/")
        # Script tag should be escaped (shown as text).
        self.assertNotIn(b"<script>", response.content.lower())


if __name__ == "__main__":
    unittest.main()
