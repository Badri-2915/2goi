# 2GOI - Production-Grade URL Shortener

A full-stack URL shortening platform with Redis caching, click analytics, QR codes, and custom aliases. Built with React, FastAPI, Redis, and Supabase PostgreSQL.

**Live URLs:**
- Short links: `https://2goi.in/abc12`
- Dashboard: `https://app.2goi.in`
- API Docs: `https://api.2goi.in/api/docs`

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite + TailwindCSS |
| Backend | FastAPI (Python) |
| Database | Supabase PostgreSQL |
| Cache | Redis |
| Auth | Supabase Auth (JWT) |
| Frontend Hosting | Vercel (free) |
| Backend Hosting | Google Cloud Run (free tier) |
| Domain | 2goi.in (GoDaddy) |

---

## Project Structure

```
windsurf-project/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Environment settings
│   │   ├── database.py          # SQLAlchemy async engine
│   │   ├── redis_client.py      # Redis connection
│   │   ├── auth.py              # JWT verification + user management
│   │   ├── middleware.py         # Rate limiting
│   │   ├── models/              # SQLAlchemy models (Link, Click, User)
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── services/            # Business logic (shortener, analytics)
│   │   └── routers/             # API route handlers
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/          # Navbar, ShortenForm, ProtectedRoute
│   │   ├── pages/               # Home, Dashboard, Analytics, Login, Signup
│   │   ├── context/             # AuthContext (Supabase Auth)
│   │   └── lib/                 # API client, Supabase client
│   ├── vercel.json
│   └── .env
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql
└── docker-compose.yml
```

---

## Local Development Setup

### Prerequisites
- Python 3.11+ 
- Node.js 18+
- Docker & Docker Compose
- A Supabase account (free tier)

### Step 1: Supabase Setup

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Go to **SQL Editor** and run the contents of `supabase/migrations/001_initial_schema.sql`
3. Go to **Settings → API** and copy:
   - Project URL
   - `anon` public key
   - `service_role` secret key
4. Go to **Settings → API → JWT Settings** and copy the JWT Secret
5. Go to **Settings → Database → Connection string** and copy the URI (use "Session mode" pooler)

### Step 2: Configure Environment

**Backend** — Edit `backend/.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres.[ref]:[password]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://[ref].supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_ANON_KEY=eyJ...
SUPABASE_JWT_SECRET=your-jwt-secret
REDIS_URL=redis://localhost:6379/0
BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Frontend** — Edit `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://[ref].supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
```

### Step 3: Start Redis

```bash
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

Or use Docker Compose (starts both Redis and backend):
```bash
docker-compose up -d redis
```

### Step 4: Start Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be at: http://localhost:8000  
API docs at: http://localhost:8000/api/docs

### Step 5: Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be at: http://localhost:5173

---

## API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/shorten` | Optional | Create a short URL |
| GET | `/{short_code}` | No | Redirect to original URL |
| GET | `/api/links` | Required | List user's links (paginated) |
| GET | `/api/analytics/{short_code}` | Required | Get click analytics |
| DELETE | `/api/links/{id}` | Required | Soft-delete a link |
| GET | `/api/health` | No | Health check |

### POST /api/shorten
```json
{
  "url": "https://example.com/very/long/url",
  "custom_alias": "mylink",
  "expires_in": 86400
}
```

Response (201):
```json
{
  "short_url": "https://2goi.in/mylink",
  "short_code": "mylink",
  "original_url": "https://example.com/very/long/url",
  "qr_code": "base64-encoded-png...",
  "expires_at": "2024-01-02T00:00:00"
}
```

---

## Production Deployment Guide

### Step 1: Deploy Frontend to Vercel

1. Push the repo to GitHub
2. Go to [vercel.com](https://vercel.com), import the repo
3. Set **Root Directory** to `frontend`
4. Set **Framework Preset** to Vite
5. Add environment variables:
   - `VITE_API_URL` = `https://api.2goi.in`
   - `VITE_SUPABASE_URL` = your Supabase URL
   - `VITE_SUPABASE_ANON_KEY` = your anon key
6. Deploy. Add `app.2goi.in` as custom domain in Vercel settings.

### Step 2: Deploy Backend to Google Cloud Run

```bash
# Install gcloud CLI: https://cloud.google.com/sdk/docs/install
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Deploy from backend directory
gcloud run deploy twogoi-api \
  --source ./backend \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=postgresql+asyncpg://...,SUPABASE_URL=https://...,SUPABASE_SERVICE_ROLE_KEY=...,SUPABASE_ANON_KEY=...,SUPABASE_JWT_SECRET=...,REDIS_URL=redis://...,BASE_URL=https://2goi.in,FRONTEND_URL=https://app.2goi.in,ENVIRONMENT=production,CORS_ORIGINS=https://app.2goi.in"

# Map custom domain
gcloud beta run domain-mappings create \
  --service twogoi-api \
  --domain api.2goi.in \
  --region asia-south1
```

### Step 3: Set Up Redis (Cloud Memorystore)

```bash
gcloud redis instances create twogoi-redis \
  --size=1 \
  --region=asia-south1 \
  --tier=basic

# Create VPC connector for Cloud Run → Redis
gcloud compute networks vpc-access connectors create twogoi-connector \
  --region=asia-south1 \
  --range=10.8.0.0/28

# Update Cloud Run to use the connector
gcloud run services update twogoi-api \
  --vpc-connector=twogoi-connector \
  --region=asia-south1
```

### Step 4: DNS Configuration (GoDaddy)

Add these DNS records for `2goi.in`:

| Type | Host | Value | TTL |
|------|------|-------|-----|
| A | @ | Cloud Run IP (from domain mapping) | 600 |
| CNAME | app | cname.vercel-dns.com | 600 |
| CNAME | api | ghs.googlehosted.com | 600 |
| TXT | @ | Google site verification token | 600 |

### Step 5: Verify

```bash
# Check DNS propagation
dig 2goi.in
dig app.2goi.in
dig api.2goi.in

# Test API
curl https://api.2goi.in/api/health

# Test redirect
curl -I https://2goi.in/test
```

---

## Architecture Highlights

- **Redis Cache-Aside Pattern** — Redirects check Redis first (sub-5ms), fall back to PostgreSQL on miss, then prime the cache
- **Async Background Tasks** — Click analytics are logged via FastAPI BackgroundTasks so redirects are never delayed
- **Base62 Encoding** — 5-char codes using `[a-zA-Z0-9]` = 916M+ unique URLs
- **Stateless Backend** — Horizontally scalable on Cloud Run with auto-scaling
- **Rate Limiting** — 100 req/min (anon) / 1000 req/min (auth) via SlowAPI middleware
- **JWT Auth** — Supabase Auth issues tokens, FastAPI validates them
- **Soft Deletes** — Links are deactivated, not removed, preserving analytics history

---

## Monthly Cost

| Service | Cost |
|---------|------|
| Domain (2goi.in) | ~₹67/month |
| Vercel (frontend) | Free |
| Cloud Run (backend) | Free (2M req/month) |
| Supabase (database) | Free (500MB) |
| Redis (Memorystore) | Free or ~₹300/month |
| **Total** | **~₹67/month** |
