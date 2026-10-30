# Deployment Guide for Public Posts Application on Render

## Overview

This application runs as a Django WSGI service with a PostgreSQL database and background worker for processing email tasks.

## Minimum Production Requirements

- **Django**: 4.2 or later
- **Python**: 3.10 or later
- **PostgreSQL**: Managed by Render's Database service
- **Gunicorn**: For serving WSGI application
- **Render Free Plan**: Web service (free) + PostgreSQL Starter plan

## Pre-deployment Checklist

1. Complete all development work locally and test.
2. Run database migrations with `python manage.py migrate`.
3. Verify email configuration works in production SMTP settings.
4. Set environment variables before deploying.

## Render Deployment Steps

### 1. Push Code to Repository

```bash
cd /home/anderson/prj/render-minimum
git add .
git commit -m "Add public posts application"
git push origin main
```

### 2. Create PostgreSQL Database in Render Dashboard

1. Go to https://dashboard.render.com/new/resource
2. Select **PostgreSQL** template
3. Choose a name (e.g., `public-posts-db`)
4. Plan: Starter ($9/month minimum) or Hobby (free tier with limitations)
5. Click "Create" - wait for provisioning

### 3. Create Web Service in Render Dashboard

1. Go to **New** → **Web Service**
2. Select your Git repository or upload your code
3. Configure:
   - **Name**: `public-posts-web`
   - **Provider**: Git (select your repo) or File Upload
   - **Build command**: `cd /opt/app/render_minimum && pip install -r requirements.txt`
   - **Start command**: `gunicorn --bind 0.0.0.0:8000 --workers 2 render_minimum.wsgi:application`
   - **Runtime**: Python
4. In environment variables, set:
   ```
   DJANGO_DEBUG=false
   PUBLIC_BASE_URL=https://your-subdomain.onrender.com
   DATABASE_URL=postgresql://${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DATABASE}?sslmode=require
   MODERATOR_EMAIL=yourmoderator@example.com
   DEFAULT_FROM_EMAIL=noreply@local
   EMAIL_COOLDOWN_SECONDS=600
   AI_CLASSIFIER_RESULT_DOUBTFUL_FIRST=true
   ```

### 4. Create Background Worker Service

1. **New** → **Background Task**
2. Configure:
   - **Name**: `public-posts-worker`
   - Same build command as web service
   - **Start command**: `python manage.py worker --queue-timeout 300 --max-claims 10`
   - Runtime: Python
   - Instance size: Small (same as web)

### 5. Link PostgreSQL Database

In each service's environment variables, add:

```bash
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/${POSTGRES_DATABASE}
```

Render will populate these values when you select the database service as a resource.

### 6. Configure Email Provider

For SMTP email delivery:

1. Set `EMAIL_HOST` (e.g., `smtp.gmail.com`, `sendgrid.net`)
2. Set `EMAIL_PORT` (e.g., `587` for TLS)
3. Set `EMAIL_USE_TLS=true`
4. Add your credentials if needed

For Gmail:
- Use App Passwords, not your main password
- Enable "Less secure apps" or use OAuth2

Alternative providers:
- **SendGrid**: Requires API key as password
- **Mailgun**: SMTP settings from dashboard
- **SES**: AWS Simple Email Service endpoint

### 7. Run Migrations After Deployment

Render automatically runs `migrate` on startup. To verify:

1. In the web service logs, check for migration output
2. Or trigger manually via the worker service logs

## Environment Variables Reference

| Variable | Purpose | Example Value |
|----------|---------|---------------|
| `DJANGO_DEBUG` | Debug mode (true for dev, false for prod) | `false` |
| `PUBLIC_BASE_URL` | Base URL for forms and emails | `https://app.onrender.com` |
| `DATABASE_URL` | PostgreSQL connection string | Auto-filled by Render |
| `MODERATOR_EMAIL` | Moderation notifications email | `moderator@example.com` |
| `DEFAULT_FROM_EMAIL` | From address in emails | `noreply@local` |
| `EMAIL_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_USE_TLS` | Use TLS encryption | `true` |
| `EMAIL_COOLDOWN_SECONDS` | Email cooldown window | `600` |
| `AI_CLASSIFIER_RESULT_DOUBTFUL_FIRST` | AI result for initial impl | `true` |

## Production Security Checklist

- [ ] `DJANGO_DEBUG=false` in production
- [ ] `ALLOWED_HOSTS` configured (don't use wildcard `*`)
- [ ] HTTPS enabled (automatic on Render)
- [ ] No secrets in code - all in environment variables
- [ ] CORS headers configured if needed
- [ ] Static files served correctly

## Known Limitations in Production

1. **Email Delivery Delays**: If SMTP is slow or fails, confirmation links may expire before delivery. Consider increasing `CONFIRMATION_DEADLINE_SECONDS`.

2. **No Free PostgreSQL on Render**: The database requires a paid plan (Starter $9/month minimum). Hobby tier with free database has limitations.

3. **Worker Process Limits**: Background workers have limited CPU/time in free plans. Consider scaling to Small instances if processing is heavy.

4. **Static Files**: Django serves static files automatically for small apps. For larger file counts, consider Cloudflare or a CDN.

## Monitoring and Maintenance

### Check Application Health

- Visit `https://your-domain.com/health/`
- Check logs in Render Dashboard → Services → Logs

### Monitor Task Queue

Run the inspect command periodically:
```bash
python manage.py inspect-failed
```

### Cleanup Expired Data

Run cleanup weekly:
```bash
python manage.py cleanup
```

Or let the worker handle it automatically.

## Troubleshooting

### Posts not appearing

1. Check `state` field in database - must be `PUBLIC` (3).
2. Verify email confirmation was completed within 60 seconds.
3. Check worker logs for processing errors.

### Emails not sending

1. Check `EMAIL_HOST` and credentials.
2. Verify SMTP connection from Render environment.
3. Check Render service logs for connection errors.

### Database migration errors

```bash
python manage.py migrate --noinput
```

### Static files missing in production

- Django includes static files by default for small apps.
- For large deployments, configure `STATIC_ROOT` and `WhiteNoiseStorage`.

## Next Steps

After deployment:

1. Test the full workflow: submit → receive email → confirm → wait for moderation → approve.
2. Monitor moderation queue - respond to requests promptly.
3. Configure custom email provider if needed.
4. Set up monitoring alerts for failed tasks.
