"""
Django admin configuration for managing posts and tasks.

This provides a simple interface for:
- Viewing and managing posts in different states.
- Inspecting confirmation and moderator tokens (hashed only).
- Queue management for email tasks.
- Cleanup of expired items.

Do not expose sensitive information like raw tokens or emails to untrusted admins.
"""

from django.contrib import admin
from .models import Post, ConfirmationToken, ModeratorToken, EmailTaskQueue, TaskLog


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin interface for posts."""
    list_display = [
        "state_name",
        "username",
        "created_at",
        "text_preview",
    ]
    list_filter = ["state"]
    search_fields = ["text", "username", "author_email"]
    readonly_fields = [
        "text",
        "username",
        "author_email",
        "created_at",
        "confirmed_at",
        "published_at",
        "state_name",
    ]

    fieldsets = (
        ("Post Information", {
            "fields": ("text", "username", "author_email"),
        }),
        ("Timestamps", {
            "fields": ("created_at", "confirmed_at", "published_at"),
        }),
        ("State", {
            "fields": ("state_name",),
        }),
    )

    def state_name(self, obj):
        """Return the readable state name."""
        return obj.state_name
    state_name.short_description = "State"

    def text_preview(self, obj):
        """Return a truncated preview of the post text."""
        preview = obj.text[:80] + "..." if len(obj.text) > 80 else obj.text
        return preview
    text_preview.short_description = "Text Preview"


@admin.register(ConfirmationToken)
class ConfirmationTokenAdmin(admin.ModelAdmin):
    """Admin interface for confirmation tokens."""
    list_display = [
        "post",
        "token_hash_short",
        "expires_at",
        "is_expired",
        "consumed",
    ]
    readonly_fields = ["post", "token_hash", "expires_at", "consumed"]

    def token_hash_short(self, obj):
        """Return the first 8 characters of the hash for display."""
        return obj.token_hash[:8] + "..."
    token_hash_short.short_description = "Token Hash (partial)"

    def is_expired(self, obj):
        """Return whether the token has expired."""
        return obj.is_expired
    is_expired.boolean = True


@admin.register(ModeratorToken)
class ModeratorTokenAdmin(admin.ModelAdmin):
    """Admin interface for moderator tokens."""
    list_display = [
        "post",
        "token_hash_short",
        "expires_at",
        "is_expired",
    ]
    readonly_fields = ["post", "token_hash", "expires_at"]

    def token_hash_short(self, obj):
        """Return the first 8 characters of the hash for display."""
        return obj.token_hash[:8] + "..."
    token_hash_short.short_description = "Token Hash (partial)"

    def is_expired(self, obj):
        """Return whether the token has expired."""
        return obj.is_expired
    is_expired.boolean = True


@admin.register(EmailTaskQueue)
class EmailTaskQueueAdmin(admin.ModelAdmin):
    """Admin interface for email task queue."""
    list_display = [
        "post",
        "recipient_email",
        "subject_preview",
        "status",
        "created_at",
    ]
    readonly_fields = ["post", "recipient_email", "subject", "body"]
    search_fields = ["recipient_email", "subject"]

    def subject_preview(self, obj):
        """Return a truncated subject line."""
        preview = obj.subject[:60] + "..." if len(obj.subject) > 60 else obj.subject
        return preview
    subject_preview.short_description = "Subject"


@admin.register(TaskLog)
class TaskLogAdmin(admin.ModelAdmin):
    """Admin interface for task execution logs."""
    list_display = [
        "task_type",
        "status",
        "details_preview",
        "created_at",
    ]
    readonly_fields = ["task_type", "status", "details"]
    search_fields = ["details"]

    def details_preview(self, obj):
        """Return a truncated log entry."""
        preview = obj.details[:100] + "..." if len(obj.details) > 100 else obj.details
        return preview
    details_preview.short_description = "Details"


@admin.register(CooldownRecord)
class CooldownRecordAdmin(admin.ModelAdmin):
    """Admin interface for cooldown records."""
    list_display = [
        "email",
        "expires_at",
        "is_expired",
    ]
    readonly_fields = ["email", "expires_at"]

    def is_expired(self, obj):
        """Return whether the cooldown has expired."""
        return obj.is_expired
    is_expired.boolean = True
