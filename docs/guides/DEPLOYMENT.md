# LLMLab Deployment Guide

Deploy LLMLab to production in 15 minutes.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer                           │
├─────────────┬──────────────────────────┬───────────────────┤
│   Browser   │     Python CLI           │     Python SDK    │
│ (React App) │  (llmlab commands)       │  (Decorators)     │
│ Vercel      │  (Local or Global)       │  (Context Mgr)    │
└─────────────┴──────────────────────────┴───────────────────┘
              │
              │ HTTPS REST API
              ▼
┌─────────────────────────────────────────────────────────────┐
│               FastAPI Backend (Railway)                     │
├─────────────────────────────────────────────────────────────┤
│  GET  /health                      (Uptime monitoring)      │
│  POST /api/auth/signup             (User creation)         │
│  POST /api/auth/login              (Authentication)        │
│  POST /api/events/track            (Cost logging)          │
│  GET  /api/costs/summary           (Dashboard data)        │
│  GET  /api/budgets, POST /budgets  (Budget management)     │
│  GET  /api/recommendations        (Cost optimization)     │
└─────────────────────────────────────────────────────────────┘
              │
              │ PostgreSQL Connection
              ▼
┌─────────────────────────────────────────────────────────────┐
│           Supabase PostgreSQL Database                      │
├─────────────────────────────────────────────────────────────┤
│  users | cost_events | budgets | (extensible tables)       │
└─────────────────────────────────────────────────────────────┘
```

---

## Deployment Steps

### 1. Backend Deployment (Railway)

#### 1a. Create Railway Account
```bash
# Go to railway.app, sign in with GitHub
```

#### 1b. Create Project
```bash
# New Project → GitHub → Select llmlab repo
# Or use Railway CLI:
railway init
```

#### 1c. Set Environment Variables
```bash
# In Railway dashboard:
DATABASE_URL=postgresql://user:pass@db.railway.internal/dbname
SUPABASE_URL=https://YOUR-PROJECT.supabase.co
SUPABASE_KEY=YOUR_SUPABASE_ANON_KEY
SECRET_KEY=your-random-secret-key-here
ALGORITHM=HS256
```

#### 1d. Configure Railway Plugin
```bash
# Add PostgreSQL plugin in Railway dashboard
# Or configure to use Supabase
```

#### 1e. Deploy
```bash
# Push to main branch (auto-deploys) or
railway deploy
```

### 2. Frontend Deployment (Vercel)

#### 2a. Create Vercel Account
```bash
# Go to vercel.com, sign in with GitHub
```

#### 2b. Import Project
```bash
# Connect GitHub → Select llmlab repo
# Select "frontend" as root directory
```

#### 2c. Set Environment Variables
```bash
NEXT_PUBLIC_API_URL=https://your-railway-backend.railway.app
```

#### 2d. Deploy
```bash
# Auto-deploys on git push, or:
vercel deploy --prod
```

### 3. Database Setup (Supabase)

#### 3a. Create Supabase Project
```bash
# Go to supabase.com
# Create project with PostgreSQL
# Copy URL and anon key
```

#### 3b. Create Tables
```bash
# In Supabase SQL editor, run:
# See schema.sql below
```

#### 3c. Set Up Auth
```bash
# Enable Email/Password auth in Supabase dashboard
```

---

## Database Schema

Create these tables in Supabase SQL editor:

```sql
-- Users table
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  hashed_password TEXT NOT NULL,
  api_key TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  monthly_budget FLOAT DEFAULT 0,
  budget_alert_threshold FLOAT DEFAULT 0.8
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_api_key ON users(api_key);

-- Cost events table
CREATE TABLE cost_events (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  provider TEXT NOT NULL,
  model TEXT NOT NULL,
  input_tokens INTEGER NOT NULL,
  output_tokens INTEGER NOT NULL,
  cost FLOAT NOT NULL,
  timestamp TIMESTAMP DEFAULT NOW(),
  metadata TEXT
);

CREATE INDEX idx_cost_events_user_timestamp ON cost_events(user_id, timestamp DESC);
CREATE INDEX idx_cost_events_timestamp ON cost_events(timestamp DESC);

-- Budgets table
CREATE TABLE budgets (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  month TEXT NOT NULL,
  budget_amount FLOAT NOT NULL,
  alert_sent BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_budgets_user_month ON budgets(user_id, month);
```

---

## CLI Deployment (PyPI)

### Setup for PyPI Release

```bash
# Create setup.py in llmlab/ root
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="llmlab-cli",
    version="0.1.0",
    description="Free LLM Cost Tracking & Optimization",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
        "tabulate>=0.9",
    ],
    entry_points={
        "console_scripts": [
            "llmlab=llmlab.cli:cli",
        ],
    },
    author="Ariv",
    author_email="hello@llmlab.dev",
    url="https://github.com/ArivunidhiA/llmlab",
)
EOF
```

### Publish to PyPI

```bash
# Build
python setup.py sdist bdist_wheel

# Install twine
pip install twine

# Upload
twine upload dist/*
```

### Verify Installation

```bash
pip install llmlab-cli
llmlab --version
```

---

## Environment Checklist

### Backend (.env)
```
DATABASE_URL=postgresql://...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
SECRET_KEY=generate-random-32-char-key
ALGORITHM=HS256
RAILWAY_ENVIRONMENT=production
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=https://your-backend-railway.app
```

### CLI (~/.llmlab/config.json) - Auto-generated
```json
{
  "api_key": "llmlab_xxx",
  "api_url": "https://your-backend-railway.app"
}
```

---

## Monitoring & Uptime

### Health Check
```bash
# Backend health
curl https://your-backend.railway.app/health

# Should return:
{
  "status": "healthy",
  "timestamp": "2026-02-09T...",
  "database": "connected"
}
```

### Keep-Alive Ping
```bash
# Railway will scale down unused apps after 15 min
# Solution: Add a cron job to ping /health every 10 min

# In your crontab:
*/10 * * * * curl https://your-backend.railway.app/health
```

Or use a service like Uptime Robot (free tier available).

---

## Troubleshooting

### Issue: 502 Bad Gateway
**Cause:** Backend crashed or not deployed  
**Fix:**
```bash
railway logs --tail
# Or check Vercel dashboard for error logs
```

### Issue: Database Connection Failed
**Cause:** Wrong DATABASE_URL  
**Fix:**
```bash
# Verify in Railway:
railway env DATABASE_URL
# Should be postgres://...
```

### Issue: CORS Errors
**Fix:** FastAPI CORS is configured for all origins
```python
# In main.py, CORS middleware is set:
allow_origins=["*"]
```

### Issue: CLI not found
**Fix:**
```bash
# Reinstall
pip uninstall llmlab-cli
pip install llmlab-cli

# Or install from local:
cd llmlab && pip install -e .
```

---

## Performance Optimization

### Database
- Add indexes on frequently queried columns (already done in schema)
- Archive old cost events to save space

### API
- Add Redis caching for /api/costs/summary
- Batch cost event inserts

### Frontend
- Enable image optimization in Next.js
- Use dynamic imports for heavy components

---

## Security

- ✅ Passwords hashed with bcrypt
- ✅ JWT tokens with expiration
- ✅ API key generation (random 32-char hex)
- ✅ CORS configured
- ✅ SQL injection protected (ORM + parameterized queries)
- 🔲 Add rate limiting (future)
- 🔲 Add 2FA (future)

---

## Rollback Plan

If something breaks:

```bash
# Railway
railway rollback  # Reverts to previous deployment

# Vercel
# Go to dashboard → Deployments → Rollback button

# Database
# Supabase has automated backups (14-day retention)
```

---

## Cost Estimation

**Free Tier (startup):**
- Vercel Frontend: $0 (free tier)
- Railway Backend: $0 (if low traffic)
- Supabase DB: $0 (free tier up to 500MB)
- Total: **$0**

**Paid Tier (scaling):**
- Vercel: $20/month (Pro)
- Railway: $5-100/month (usage-based)
- Supabase: $25+/month (Pro)
- Total: **$50-150/month**

---

## Next Steps

1. Deploy backend to Railway
2. Deploy frontend to Vercel
3. Set up Supabase database
4. Verify all endpoints working
5. Release CLI to PyPI
6. Announce on HN, ProductHunt, Reddit
7. Monitor logs and user feedback
8. Iterate fast

---

**You're now ready to deploy! 🚀**
