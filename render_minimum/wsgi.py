"""
WSGI entry point for the Django application.

This module is imported by gunicorn to start the web server in production.
"""

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "render_minimum.settings")

# Create the WSGI application.
application = get_wsgi_application()

# Apply database migrations.
from django.core.management import call_command
call_command("migrate", "--noinput", verbosity=0)
