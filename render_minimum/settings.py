"""
Django settings for render_minimum application.

Do not store secrets in this file. Use environment variables instead.
For local development, create a .env.local file with the same variable names.
"""

import os
from pathlib import Path

# Build paths inside the project.
BASE_DIR = Path(__file__).resolve().parent.parent

# Application name.
SITE_ID = 1

# SECURITY WARNING: Don't run with debug on in production.
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"

# Allowed hosts for protection against Host header attacks.
# Use a wildcard (*) only in development. Configure properly in production.
ALLOWED_HOSTS = [
    "*",  # Development: allow all hosts
]

# CSRF trusted origins for cross-site requests.
CSRF_TRUSTED_ORIGINS = []  # Production: add specific domains here if needed

# Application definition.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "render_minimum.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "render_minimum" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "render_minimum.wsgi.application"

# Database configuration - SQLite for local development, PostgreSQL for production.
DATABASES = {
    "default": {}
}

# Use SQLite for local development.
if "DATABASE_URL" not in os.environ:
    DATABASES["default"].update({
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    })
else:
    # Parse PostgreSQL connection string from environment variable.
    # Format: postgres://user:password@host:port/database?options
    from urllib.parse import parse_qs, urlparse
    db_url = os.getenv("DATABASE_URL")
    parsed = urlparse(db_url)
    query_params = parse_qs(parsed.query)
    DATABASES["default"].update({
        "ENGINE": "django.db.backends.postgresql",
        "NAME": parsed.path.lstrip("/"),
        "USER": parsed.username,
        "PASSWORD": parsed.password,
        "HOST": parsed.hostname,
        "PORT": str(parsed.port) if parsed.port else "5432",
        "OPTIONS": {
            "sslmode": "require" if query_params.get("sslmode") else "prefer",
        },
    })

# Password validation - not needed since we don't use passwords.
AUTH_PASSWORD_VALIDATORS = []

# Authentication backends - using the default model backend.
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

# Custom user model - simplified without email verification or unique usernames.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class SimpleUser(AbstractBaseUser, PermissionsMixin):
    """Simplified user model for post authors."""
    email = models.EmailField("email address", max_length=254)
    is_staff = False
    is_active = True

    USERNAME_FIELD = "email"

    class Meta:
        verbose_name = "simple user"
        verbose_name_plural = "simple users"


# Login/Logout URLs.
LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_URL = "account_logout"

# Static files (CSS, JavaScript, images) - Django serves these in development.
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "render_minimum" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files - user uploads and similar content.
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Internationalization settings.
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Security settings.
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Session cookie settings - secure by default.
SESSION_COOKIE_SECURE = not DEBUG  # Only use HTTPS cookies in production
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Email backend - Django console email for development, SMTP for production.
EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend"  # Development: print to console
    if DEBUG
    else "django.core.mail.backends.smtp.EmailBackend"
)

# EMAIL_HOST and EMAIL_PORT from environment in production.
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 30

# Base URL for building links in emails and forms. Must be set in production.
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")

# Email addresses - moderator receives review notifications.
MODERATOR_EMAIL = os.getenv("MODERATOR_EMAIL", "moderator@example.com")

# Message classes for email.
DEFAULT_FROM_EMAIL = "noreply@local"  # Customize in .env

# Timeouts and deadlines.
CONFIRMATION_DEADLINE_SECONDS = 60  # Post must be confirmed within this time
MODERATOR_TOKEN_TTL_HOURS = 24      # Moderator link expires after this duration

# Email cooldown period - temporary email block.
EMAIL_COOLDOWN_SECONDS = 600        # 10 minutes between submissions from same email

# Rate limiting - requests per minute per email.
RATE_LIMIT_WINDOW = 60              # seconds
RATE_LIMIT_REQUESTS = 3             # maximum submissions in the window

# Worker settings.
TASK_LEASE_SECONDS = 300            # Task claim lease duration
TASK_MAX_ATTEMPTS = 3               # Maximum retry attempts before marking failed
AI_CLASSIFIER_RESULT_DOUBTFUL_FIRST = True   # Initial implementation always returns DOUBTFUL

# Static files storage in production - Render serves static files.
# STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
