# LLMLab Deployment Guide

This guide covers deployment to **Railway** (backend), **Vercel** (frontend), and **Supabase** (database).

---

## Prerequisites

- GitHub account with auth token in `.env`
- Railway account (https://railway.app) — FREE tier available
- Vercel account (https://vercel.com) — FREE tier available
- Supabase account (https://supabase.com) — FREE tier available
- Node.js 18+ installed locally
- Python 3.9+ installed locally

---

## Step 1: Local Development Setup

### Backend (FastAPI)

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your values

# Run tests
pytest

# Run server locally
uvicorn main:app --reload
# Open http://localhost:8000/health
```

### Frontend (React/Next.js)

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cp .env.example .env.local
# Edit .env.local with your values

# Run development server
npm run dev
# Open http://localhost:3000
```

### CLI

```bash
cd cli

# Install in development mode
pip install -e .

# Test commands
llmlab --version
llmlab init
```

---

## Step 2: Database Setup (Supabase)

### Create Supabase Project

1. Go to https://supabase.com
2. Click "New project"
3. Select your region (closest to you)
4. Name: `llmlab`
5. Create strong password
6. Click "Create new project"
7. Wait 2-3 minutes for setup

### Load Database Schema

1. Copy your **Connection string** from Supabase dashboard (PostgreSQL tab)
2. Connect to database:
   ```bash
   psql postgresql://[user]:[password]@[project].supabase.co:5432/postgres
   ```
3. Run schema:
   ```bash
   psql < docs/DATABASE_SCHEMA.sql
   ```
4. Verify tables created:
   ```sql
   \dt
   ```

### Get Database URL

1. Go to Supabase dashboard → Settings → Database
2. Copy **Connection string** (PostgreSQL)
3. Format: `postgresql://[user]:[password]@[host]:[port]/[database]`
4. Save for later (needed for Railway)

---

## Step 3: Deploy Backend to Railway

### Option A: Manual (Recommended)

1. **Create Railway Project**
   - Go to https://railway.app
   - Click "New Project"
   - Select "GitHub Repo"
   - Authorize and select `ArivunidhiA/llmlab`

2. **Configure Services**
   - Railway will auto-detect it's Python
   - Add environment variables:
     - `DATABASE_URL` = (from Supabase)
     - `JWT_SECRET` = (generate random: `openssl rand -hex 32`)
     - `API_KEYS` = `demo` (can add more later)
     - `ENVIRONMENT` = `production`

3. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Get domain: `https://llmlab-backend.up.railway.app`

4. **Test**
   ```bash
   curl https://llmlab-backend.up.railway.app/health
   # Should return: {"status": "healthy", ...}
   ```

### Option B: Using Railway CLI

```bash
# Login to Railway
railway login

# Create new project
railway init

# Set environment variables
railway variables set DATABASE_URL=postgresql://...
railway variables set JWT_SECRET=your-secret
railway variables set API_KEYS=demo

# Deploy
railway deploy backend/

# Get URL
railway domains
```

### Environment Variables

```env
DATABASE_URL=postgresql://user:password@host:5432/postgres
JWT_SECRET=your-random-secret-here
API_KEYS=demo
ENVIRONMENT=production
CORS_ORIGINS=https://llmlab-frontend.vercel.app,http://localhost:3000
```

---

## Step 4: Deploy Frontend to Vercel

### Option A: Web Dashboard (Easiest)

1. **Create Vercel Account**
   - Go to https://vercel.com
   - Click "Sign up"
   - Select "Continue with GitHub"
   - Authorize

2. **Import Project**
   - Click "New Project"
   - Select `ArivunidhiA/llmlab`
   - Configure:
     - **Root Directory**: `frontend`
     - **Environment Variable**:
       - `NEXT_PUBLIC_API_URL` = `https://llmlab-backend.up.railway.app`

3. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Get domain: `https://llmlab.vercel.app`

4. **Test**
   - Open https://llmlab.vercel.app
   - Should load landing page

### Option B: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy from frontend directory
cd frontend
vercel --prod

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL
# Enter: https://llmlab-backend.up.railway.app

# Re-deploy with env var
vercel --prod
```

### Environment Variables (Frontend)

```env
NEXT_PUBLIC_API_URL=https://llmlab-backend.up.railway.app
NEXT_PUBLIC_APP_NAME=LLMLab
```

---

## Step 5: Connect Services

### Update Frontend API URL

In `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=https://llmlab-backend.up.railway.app
```

Then redeploy to Vercel.

### Update Backend CORS

In `backend/main.py`, update CORS origins:
```python
CORSMiddleware(
    app,
    allow_origins=[
        "https://llmlab.vercel.app",
        "http://localhost:3000",
    ],
    ...
)
```

Then push to GitHub, Railway auto-deploys.

### Test End-to-End

```bash
# 1. Create account via frontend
# Open https://llmlab.vercel.app
# Click "Sign Up"
# Email: test@example.com, Password: test123

# 2. Check backend received it
curl -X POST https://llmlab-backend.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'

# Should return token and user_id
```

---

## Step 6: Publish CLI to PyPI

### Setup PyPI Account

1. Go to https://pypi.org
2. Click "Register"
3. Create account
4. Go to Account Settings → API tokens
5. Create token → Save it

### Build and Upload

```bash
cd cli

# Build distribution
python setup.py sdist bdist_wheel

# Install twine (if not installed)
pip install twine

# Upload to PyPI
twine upload dist/*

# When prompted, username = `__token__`, password = your token
```

### Test Installation

```bash
# In a new directory
pip install llmlab-cli

# Test
llmlab --version
# Should print: llmlab, version 0.1.0
```

---

## Step 7: Configure Monitoring

### Railway Monitoring

1. Go to Railway dashboard
2. Select `llmlab` project
3. Click "Deployments"
4. Monitor logs, memory, CPU

### Vercel Analytics

1. Go to Vercel dashboard
2. Select `llmlab` project
3. Click "Analytics"
4. Monitor page load times, CLS, etc.

### Supabase Monitoring

1. Go to Supabase dashboard
2. Click "Monitoring"
3. Monitor database connections, queries, etc.

---

## Step 8: Setup Auto-Deployments

### Backend (Railway)

Already auto-deploys on every git push to `main` or `dev`.

To disable:
- Go to Railway project settings
- Disable "Auto-deploy"

### Frontend (Vercel)

Already auto-deploys on every git push to `main` or `dev`.

To disable:
- Go to Vercel project settings
- Disable "Automatic Deployments"

---

## Troubleshooting

### Backend Won't Deploy

```bash
# Check Railway logs
railway logs

# Common issues:
# 1. Missing DATABASE_URL
#    → Add environment variable in Railway dashboard
# 2. Database migrations failed
#    → Run: psql < docs/DATABASE_SCHEMA.sql
# 3. Python version mismatch
#    → Add runtime.txt: "python-3.11.7"
```

### Frontend Won't Deploy

```bash
# Check Vercel logs
vercel logs [project-name]

# Common issues:
# 1. Missing NEXT_PUBLIC_API_URL
#    → Add environment variable in Vercel dashboard
# 2. Build failed
#    → Run locally: npm run build
# 3. Port conflicts
#    → Vercel handles port automatically
```

### Database Connection Failed

```bash
# Test connection locally
psql postgresql://[user]:[password]@[host]:[port]/postgres

# Common issues:
# 1. Wrong connection string format
#    → Use: postgresql://user:password@host:port/database
# 2. Firewall blocking connection
#    → Supabase whitelist Railway IP
# 3. Database not created
#    → Create new Supabase project
```

---

## Performance Optimization

### Backend

```python
# Add caching
from fastapi import cache
from functools import lru_cache

@app.get("/api/costs/summary")
@cache(expire=300)  # Cache for 5 minutes
async def get_costs(user_id):
    ...
```

### Frontend

```javascript
// Add SWR caching
import useSWR from 'swr'

function CostDashboard() {
  const { data } = useSWR('/api/costs/summary', fetcher, {
    revalidateOnFocus: false,  // Don't refetch on tab focus
    revalidateOnReconnect: true,  // Refetch on reconnect
  })
  ...
}
```

### Database

```sql
-- Add indexes for frequently-accessed columns
CREATE INDEX idx_cost_events_user_id ON cost_events(user_id);
CREATE INDEX idx_cost_events_timestamp ON cost_events(timestamp);
```

---

## Security Checklist

- ✅ All secrets stored in environment variables (not in code)
- ✅ HTTPS enforced (automatic with Railway/Vercel)
- ✅ CORS configured (only allow frontend domain)
- ✅ JWT tokens set to expire in 24 hours
- ✅ Passwords hashed with bcrypt
- ✅ Database backups enabled (Supabase automatic)
- ✅ Rate limiting on API (100 req/min per key)
- ✅ Input validation on all endpoints (Pydantic)

---

## Rollback

### Backend

```bash
# Go to Railway dashboard
# Select deployment
# Click "Rollback"
# Confirm
```

### Frontend

```bash
# Go to Vercel dashboard
# Click "Deployments"
# Find previous deployment
# Click "Restore"
```

---

## Cost Estimation

| Service | Tier | Cost |
|---------|------|------|
| Railway | Free | $0 |
| Vercel | Free | $0 |
| Supabase | Free | $0 |
| **Total** | | **$0** |

All services offer generous free tiers that will support 1000+ users.

---

## Next Steps

1. ✅ Deployed backend to Railway
2. ✅ Deployed frontend to Vercel
3. ✅ Deployed database to Supabase
4. ✅ Published CLI to PyPI
5. Launch publicly!

See `LAUNCH_CHECKLIST.md` for next steps.
