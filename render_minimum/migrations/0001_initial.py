# Generated manually - defines the initial database schema for all models.

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0011_update_permissions"),  # Django default auth migration.
    ]

    operations = [
        # SimpleUser model (optional, for email notifications).
        migrations.CreateModel(
            name="SimpleUser",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False)),
                ("email", models.EmailField(max_length=254, unique=True, verbose_name="email address")),
                ("is_staff", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("date_joined", models.DateTimeField(verbose_name="date joined")),
            ],
            options={
                "verbose_name": "simple user",
                "verbose_name_plural": "simple users",
            },
        ),

        # Post model - main content object.
        migrations.CreateModel(
            name="Post",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("text", models.TextField(help_text="Content of the post (1-3000 characters).")),
                ("username", models.CharField(max_length=40, help_text="Display name for the poster (2-40 characters).")),
                ("author_email", models.EmailField(help_text="Email address of the post author.")),
                ("created_at", models.BigIntegerField(default=models.fields.DateTimeField.now, help_text="Unix timestamp when the post was created.")),
                ("confirmed_at", models.BigIntegerField(null=True, blank=True)),
                ("published_at", models.BigIntegerField(null=True, blank=True)),
                ("state", models.SmallIntegerField(choices=[(1, "AWAITING_CONFIRMATION"), (2, "AWAITING_AI"), (3, "PUBLIC"), (4, "REJECTED"), (5, "AWAITING_MODERATION")], default=1)),
            ],
            options={
                "verbose_name": "post",
                "verbose_name_plural": "posts",
                "ordering": ["-created_at"],
            },
        ),

        # ConfirmationToken model - for user confirmation.
        migrations.CreateModel(
            name="ConfirmationToken",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("token_hash", models.CharField(max_length=64)),
                ("expires_at", models.BigIntegerField()),
                ("consumed", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "confirmation token",
                "verbose_name_plural": "confirmation tokens",
            },
        ),

        # ModeratorToken model - for moderation review access.
        migrations.CreateModel(
            name="ModeratorToken",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("token_hash", models.CharField(max_length=64)),
                ("expires_at", models.BigIntegerField()),
            ],
            options={
                "verbose_name": "moderator token",
                "verbose_name_plural": "moderator tokens",
            },
        ),

        # EmailTaskQueue model - queue for sending emails.
        migrations.CreateModel(
            name="EmailTaskQueue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("post", models.ForeignKey(on_delete=models.CASCADE, to="render_minimum.post")),
                ("recipient_email", models.EmailField()),
                ("subject", models.TextField()),
                ("body", models.TextField()),
                ("status", models.CharField(choices=[("pending", "pending"), ("claimed", "claimed"), ("sent", "sent"), ("failed", "failed")], default="pending", max_length=20)),
                ("created_at", models.BigIntegerField(default=models.fields.DateTimeField.now)),
                ("claimed_at", models.BigIntegerField(null=True, blank=True)),
                ("next_retry_at", models.BigIntegerField(null=True, blank=True)),
                ("attempt_count", models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                "verbose_name": "email task",
                "verbose_name_plural": "email tasks",
            },
        ),

        # CooldownRecord model - temporary email block.
        migrations.CreateModel(
            name="CooldownRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("email", models.EmailField(unique=True)),
                ("expires_at", models.BigIntegerField()),
                ("created_at", models.BigIntegerField(default=models.fields.DateTimeField.now)),
            ],
            options={
                "verbose_name": "cooldown record",
                "verbose_name_plural": "cooldown records",
            },
        ),

        # TaskLog model - task execution logs.
        migrations.CreateModel(
            name="TaskLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("task_type", models.CharField(choices=[("email", "email"), ("ai", "ai"), ("cleanup", "cleanup")], max_length=10)),
                ("status", models.CharField(max_length=20)),
                ("details", models.TextField()),
                ("created_at", models.BigIntegerField(default=models.fields.DateTimeField.now)),
            ],
            options={
                "verbose_name": "task log",
                "verbose_name_plural": "task logs",
                "ordering": ["-created_at"],
            },
        ),

    ]
