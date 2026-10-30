# Public Posts Application

A Django-based web application for text post submissions with email confirmation. Built for deployment on Render.

## Features

- **Public post listing** - View all approved posts without an account.
- **Email confirmation** - Users submit posts via email and confirm through a time-limited link.
- **AI placeholder classifier** - Initial implementation returns "DOUBTFUL" (requires manual moderation).
- **Moderation workflow** - Human reviewers approve or reject pending posts.
- **Temporary email block** - Prevents spam with 10-minute cooldown between submissions.
- **Task worker** - Processes emails and cleanup operations as a background process.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Public Posts App                      │
├─────────────────────────────────────────────────────────────┤
│  Frontend: Django templates (server-rendered)                │
│  Backend: Python Django with server-side logic                │
│  Database: PostgreSQL (production), SQLite (local)            │
│  Email: SMTP / Console backend (local)                        │
├─────────────────────────────────────────────────────────────┤
│  States:                                                      │
│    AWAITING_CONFIRMATION → CONFIRMED → AWAITING_AI           │
│                           → PUBLIC / REJECTED                  │
│    AWAITING_AI → SAFE / UNSAFE / DOUBTFUL                    │
│    DOUBTFUL → AWAITING_MODERATION                            │
│    AWAITING_MODERATION → PUBLIC / REJECTED                    │
├─────────────────────────────────────────────────────────────┤
│  Security:                                                    │
│    - Confirmation tokens (60s expiry, DB-enforced)            │
│    - Moderator tokens (24h expiry, link-based auth)           │
│    - Cooldown records (10 min between submissions)            │
│    - CSRF protection on all forms                             │
└─────────────────────────────────────────────────────────────┘
```

## Local Development Setup

### Prerequisites

- Python 3.10 or later
- PostgreSQL (recommended) or SQLite (for simple testing)
- pip installed

### Steps

1. **Clone or navigate to the project directory:**
   ```bash
   cd /home/anderson/prj/render-minimum
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or: venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a database (optional for local development):**
   ```bash
   # Using SQLite (default, no setup needed)
   python manage.py migrate

   # Or using PostgreSQL:
   # DATABASE_URL=postgres://user:pass@localhost/dbname
   python manage.py migrate
   ```

5. **Configure environment variables:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local and set your values.
   # For local dev, you can leave DATABASE_URL commented out (uses SQLite).
   ```

6. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

7. **Start the development server:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

8. **Open in browser:**
   ```
   http://localhost:8000/
   ```

## Production Deployment on Render

### Steps

1. **Create a Render account** at https://render.com

2. **Deploy the services:**
   
   Option A: Use the Blueprint file (recommended):
   ```bash
   # Upload your code to a Git repository first
   git add .
   git commit -m "Add render.yaml"
   git push
   
   # In Render Dashboard, create new resources from your repo
   ```

   Option B: Manual deployment via Render Dashboard:
   
   a. **Create PostgreSQL Database:**
      - Go to Dashboard → New → PostgreSQL
      - Name: `public-posts-db`
      - Click "Create"

   b. **Create Web Service:**
      - Go to Dashboard → New → Web Service
      - Name: `public-posts-web`
      - Provider: Git Repository (or File Upload)
      - Source: Your repository with render.yaml
      - Runtime: Python
      - Build command: `cd /opt/app/render_minimum && pip install -r requirements.txt`
      - Start command: `gunicorn --bind 0.0.0.0:8000 --workers 2 render_minimum.wsgi:application`

   c. **Create Background Worker:**
      - Go to Dashboard → New → Background Task
      - Name: `public-posts-worker`
      - Runtime: Python
      - Build command: Same as web service
      - Start command: `python manage.py worker --queue-timeout 300 --max-claims 10`

   d. **Link PostgreSQL:**
      - In each service's environment variables, add:
      ```
      DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/${POSTGRES_DATABASE}
      ```

3. **Configure environment variables** in Render Dashboard for each service:
   ```
   DJANGO_DEBUG=false
   PUBLIC_BASE_URL=https://your-app.onrender.com
   MODERATOR_EMAIL=yourmoderator@example.com
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=true
   DEFAULT_FROM_EMAIL=noreply@local
   ```

4. **Set up email:**
   - For Gmail: Use an App Password (not your regular password).
   - Or use SendGrid, Mailgun, or another provider.

5. **Run migrations** after deployment:
   - Render automatically runs `migrate` on start.
   - You can also trigger manually via the worker service.

## Required Secrets

These must be set in environment variables (not in code):

| Variable | Description | Default/Required |
|----------|-------------|------------------|
| `DJANGO_DEBUG` | Debug mode (false in production) | false |
| `PUBLIC_BASE_URL` | Base URL for the application | Your domain |
| `MODERATOR_EMAIL` | Email receiving moderation notifications | moderator@example.com |
| `DEFAULT_FROM_EMAIL` | From address for emails | noreply@local |
| `EMAIL_HOST` | SMTP server hostname | smtp.gmail.com |
| `EMAIL_PORT` | SMTP port | 587 |
| `EMAIL_USE_TLS` | Use TLS for SMTP | true |
| `DATABASE_URL` | PostgreSQL connection string | Required in production |

## Testing

Run the tests:
```bash
python manage.py test
```

Or with pytest:
```bash
pip install pytest pytest-django
python -m pytest --ds=render_minimum.settings
```

## Known Limitations

1. **Confirmation deadline**: If email delivery or service startup is slow, posts may expire during the one-minute confirmation window. Consider increasing `CONFIRMATION_DEADLINE_SECONDS` for unreliable connections.

2. **Email reliability**: SMTP delivery is best-effort. Failed emails are retried up to 3 times. Posts awaiting confirmation will eventually be rejected if not confirmed.

3. **AI classifier**: Initial implementation always returns "DOUBTFUL" (requires moderation). Replace `classification_result()` in `views.py` with real AI integration.

4. **Moderator link expiry**: Moderator tokens expire after 24 hours. Links are the credential - anyone with access can make decisions.

5. **Database differences**: SQLite does not support row-level locking for concurrent writes. Use PostgreSQL in production to prevent race conditions during cooldown checks and state transitions.

## File Summary

| Path | Purpose |
|------|---------|
| `manage.py` | Django management entry point |
| `requirements.txt` | Python dependencies |
| `render.yaml` | Render deployment blueprint |
| `.env.example` | Environment variable template |
| `render_minimum/` | Application package |
| │   ├── `settings.py` | Django settings |
| │   ├── `models.py` | Database models |
| │   ├── `views.py` | View functions |
| │   ├── `urls.py` | URL routing |
| │   ├── `wsgi.py` | WSGI application entry |
| │   ├── `admin.py` | Django admin config |
| │   ├── `forms.py` | Form definitions |
| │   └── `migrations/` | Database migrations |
| │       └── `__init__.py` | Empty init file |
| │   ├── `management/` | Management commands |
| │       └── `commands/` | Worker, cleanup, inspect scripts |
| │   └── `templates/` | HTML templates |
| `README.md` | This documentation |

## License

Public domain. Free to use and modify.
