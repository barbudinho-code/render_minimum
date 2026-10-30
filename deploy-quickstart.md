# Quick Deployment on Render (15 Minutes)

## Prerequisites
- Render account: https://render.com/signin
- PostgreSQL service created ($9/month minimum for production database)

## One-Command Deploy

### Option 1: Using render.yaml Blueprint (Recommended)

```bash
cd /home/anderson/prj/render-minimum
git add .
git commit -m "Ready for production"
git push origin main
```

Then in Render Dashboard:
1. Create Web Service from your repo
2. Create Background Task from same repo  
3. Link PostgreSQL database
4. Add environment variables (see table below)

### Option 2: Manual Deployment via Dashboard

**1. Create Services:**
- Web: `public-posts-web` 
- Worker: `public-posts-worker`

**2. Build Commands (same for both):**
```bash
cd /opt/app/render_minimum && pip install -r requirements.txt
```

**3. Start Commands (different):**
```bash
# Web Service
gunicorn --bind 0.0.0.0:8000 --workers 2 render_minimum.wsgi:application

# Worker Service  
python manage.py worker --queue-timeout 300 --max-claims 10
```

## Environment Variables (Add in Render Dashboard)

```bash
DJANGO_DEBUG=false
PUBLIC_BASE_URL=https://your-app.onrender.com
MODERATOR_EMAIL=moderator@example.com
DEFAULT_FROM_EMAIL=noreply@local
EMAIL_COOLDOWN_SECONDS=600
AI_CLASSIFIER_RESULT_DOUBTFUL_FIRST=true
```

**Database (auto-filled by Render):**
```bash
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/${POSTGRES_DATABASE}
```

## Post-Deployment Testing

1. Visit `https://your-app.onrender.com/` → Should show "No public posts"
2. Submit a test post: `https://your-app.onrender.com/submit/`
3. Check email delivery works
4. Verify confirmation link activates within 60 seconds
5. Check worker processing logs

## Minimum Cost

- Web Service (Free): $0
- Worker (Free): $0  
- PostgreSQL (Starter): ~$9/month
- **Total: ~$9/month minimum**

## Troubleshooting

**Email not working?** Configure SMTP in Render Dashboard, then restart services.

**Database connection errors?** Check `DATABASE_URL` has correct credentials from your PostgreSQL service.

**Static files missing?** Django includes them by default for small apps. For larger deployments, configure `STATIC_ROOT`.

---

Need more details? See `deploy.md` or `README.md`.
