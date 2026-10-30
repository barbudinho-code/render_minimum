# Deployment Guide for Public Posts Application on Render

## Quick Start (5 Steps)

### Step 1: Prepare Your Code
```bash
cd /home/anderson/prj/render-minimum
git add .
git commit -m "Prepare for production deployment"
git push origin main
```

### Step 2: Create PostgreSQL Database
1. Go to https://dashboard.render.com/new/resource
2. Select **PostgreSQL** → Click "Create"
3. Choose name (e.g., `public-posts-db`)
4. Plan: Starter ($9/month) or Hobby (free, limited features)

### Step 3: Deploy Web Service
1. **New** → **Web Service**
2. Select your Git repository
3. Configure:
   ```
   Name: public-posts-web
   Build Command: cd /opt/app/render_minimum && pip install -r requirements.txt
   Start Command: gunicorn --bind 0.0.0.0:8000 --workers 2 render_minimum.wsgi:application
   Instance Type: Free (Small)
   ```
4. Add environment variables (see table below)
5. Click "Create Web Service"

### Step 4: Deploy Background Worker
1. **New** → **Background Task**
2. Select same Git repository
3. Configure:
   ```
   Name: public-posts-worker
   Build Command: cd /opt/app/render_minimum && pip install -r requirements.txt
   Start Command: python manage.py worker --queue-timeout 300 --max-claims 10
   Instance Type: Free (Small)
   ```
4. Same environment variables as web service
5. Click "Create Background Task"

### Step 5: Configure Environment Variables

| Variable | Required? | Example Value | Notes |
|----------|-----------|---------------|-------|
| `DJANGO_DEBUG` | Yes | `false` | Never true in production |
| `PUBLIC_BASE_URL` | Yes | `https://your-app.onrender.com` | Auto-detected if omitted |
| `DATABASE_URL` | Yes (from Render) | Auto-filled | Don't set manually |
| `MODERATOR_EMAIL` | Yes | `moderator@example.com` | Where moderation emails go |
| `DEFAULT_FROM_EMAIL` | No | `noreply@local` | From address in emails |
| `EMAIL_HOST` | Yes | `smtp.gmail.com` | Your SMTP provider |
| `EMAIL_PORT` | Yes | `587` | TLS port |
| `EMAIL_USE_TLS` | Yes | `true` | Use SSL/TLS |
| `EMAIL_COOLDOWN_SECONDS` | No | `600` | Default 10 minutes |
| `AI_CLASSIFIER_RESULT_DOUBTFUL_FIRST` | No | `true` | Initial implementation |

## Detailed Setup

### Option A: Deploy via Render Blueprint (Recommended)

Upload `render.yaml` and use Render's Blueprint feature:

```bash
# Upload your code with render.yaml
git add .
git commit -m "Add render deployment blueprint"
git push origin main
```

Render will auto-detect the Blueprint file.

### Option B: Manual Deployment via Dashboard

**1. Set up PostgreSQL Database:**
- Create in Render Dashboard
- Note connection string
- In each service, set `DATABASE_URL` from database settings

**2. Configure Email Provider:**

For Gmail (with App Password):
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-email@gmail.com  # Optional
EMAIL_HOST_PASSWORD=your-app-password  # Optional
```

For SendGrid:
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USERapikey.sendgrid.net
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

**3. Test Deployment:**
```bash
# Visit these URLs to verify deployment:
https://your-app.onrender.com/          # Main listing
https://your-app.onrender.com/health/   # Health check
```

### Environment Variable Details

**Required (must set before deployment):**
- `DJANGO_DEBUG=false`
- `PUBLIC_BASE_URL=https://your-domain.onrender.com`
- `DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/${POSTGRES_DATABASE}`
- `MODERATOR_EMAIL=moderator@example.com`

**Email settings (configure after deployment):**
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
DEFAULT_FROM_EMAIL=noreply@local
```

### Cost Estimate (Minimum Production)

| Service | Plan | Cost/month | Notes |
|---------|------|------------|-------|
| Web Service | Free | $0 | Basic free tier |
| Background Worker | Free | $0 | Basic free tier |
| PostgreSQL Database | Starter | ~$9 | Minimum for production |
| **Total** | - | **~$9/month** | Can be higher depending on database usage |

### Post-Deployment Checklist

- [ ] Run `python manage.py migrate` (Render auto-runs this)
- [ ] Test submission form at `https://your-domain.com/submit/`
- [ ] Check email delivery works
- [ ] Verify confirmation link works
- [ ] Test moderation flow
- [ ] Review application logs in Render Dashboard

### Troubleshooting Common Issues

**Email not sending:**
1. Check `EMAIL_HOST` and credentials are correct
2. For Gmail: use App Password, not regular password
3. Enable "Less secure apps" or use OAuth2 (for Gmail)
4. Check service logs for connection errors

**Database migration errors:**
```bash
# Trigger migrations manually
python manage.py migrate --noinput
```

**Static files missing:**
- Django serves static files automatically for small apps
- For large deployments, configure `STATIC_ROOT` in settings

**Worker not processing tasks:**
1. Check background task service is running
2. Look at logs for errors
3. Try manual cleanup: `python manage.py cleanup --dry-run`

### Monitoring

**Health check endpoint:**
```
https://your-domain.com/health/
```

Returns JSON with status, Django version, database engine.

**Logs:**
- Go to Render Dashboard → Services → [Service] → Logs

**Failed tasks:**
```bash
# Connect via SSH or use Render dashboard logs
python manage.py inspect-failed
```

### Security Notes

- All tokens are hashed (not stored in plain text)
- Confirmation links expire after 60 seconds
- Moderator links expire after 24 hours
- CSRF protection on all forms
- HTTPS enforced by Render
- No passwords used (email-only auth)

### Next Steps After Deployment

1. **Set up monitoring** - Add alerts for failed tasks
2. **Configure email provider** - Test SMTP delivery
3. **Test full workflow** - Submit → Confirm → Wait → Moderation
4. **Document moderation process** - Who approves posts?
5. **Set up backups** - Render handles automatic database backups

### Contact Support

If you need help:
- Render Dashboard Help Center
- Check application logs for errors
- Review `.env.example` for variable documentation
