# 2GOI - Production-Grade URL Shortener

A full-stack URL shortening service with Base62 ID encoding, Redis caching, pre-aggregated click analytics, QR codes, and custom aliases. Single-domain architecture serving frontend, API, and redirects from one process.

**Live:** [https://2goi.in](https://2goi.in)

```
https://2goi.in          Homepage
https://2goi.in/2Bq      Redirect to original URL
https://2goi.in/dashboard User dashboard
https://2goi.in/api/docs  Swagger API docs
```

---

## Architecture

```
User Request
     |
     v
FastAPI (single process)
     |
     +-- /              -> React SPA (static files)
     +-- /login, etc.   -> React SPA (client-side routing)
     +-- /api/*          -> REST API endpoints
     +-- /{short_code}   -> 302 redirect (Redis cache -> PostgreSQL fallback)
```

```
Redirect Flow:

Client -> FastAPI -> Redis Cache (hit? -> 302 redirect)
                        |
                  (miss) -> PostgreSQL -> cache URL -> 302 redirect
                        |
                  BackgroundTask -> log click + upsert daily_click_stats
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Vite + TailwindCSS |
| Backend | FastAPI + async SQLAlchemy + Gunicorn/Uvicorn |
| Database | Supabase PostgreSQL (via session pooler + SSL) |
| Cache | Redis (hot-link caching with TTL) |
| Auth | Supabase Auth (ES256 JWT verified via JWKS endpoint) |
| Hosting | Render (Docker, free tier) |
| Monitoring | UptimeRobot (5-min health pings to prevent cold starts) |
| Domain | 2goi.in (GoDaddy) |

---

## Key Engineering Decisions

- **Base62 Encoding from Sequential DB IDs** — Short codes are deterministic (`sequence_id -> Base62`), eliminating collision checks and extra DB queries. Supports 62^6 = 56B+ unique URLs.
- **Redis Cache-Aside Pattern** — Redirects check Redis first (<5ms), fall back to PostgreSQL on miss, then prime the cache. Expired links use Redis TTL for auto-eviction.
- **Async Click Analytics** — Click logging runs in `BackgroundTasks`, never blocking the redirect response.
- **Pre-Aggregated Daily Stats** — `daily_click_stats` table uses `INSERT ON CONFLICT UPDATE` (upsert) for O(1) writes and O(days) analytics reads, instead of scanning millions of raw click rows.
- **Single-Domain Architecture** — FastAPI serves React static files, API routes, and short code redirects all from `2goi.in`. No subdomains or separate deployments needed.
- **ES256 JWT Verification** — Supabase tokens verified via JWKS endpoint with PyJWT, supporting key rotation.

---

## Project Structure

```
2goi/
├── Dockerfile                    # Multi-stage: Node builds frontend -> Python serves it
├── render.yaml                   # Render Blueprint (web service + Redis)
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app + SPA serving + 404 fallback
│   │   ├── auth.py               # JWKS-based ES256 JWT verification
│   │   ├── config.py             # Environment settings
│   │   ├── database.py           # Async SQLAlchemy engine (Supabase pooler + SSL)
│   │   ├── redis_client.py       # Redis connection manager
│   │   ├── middleware.py         # Rate limiting (SlowAPI)
│   │   ├── models/               # Link, Click, User, DailyClickStats
│   │   ├── schemas/              # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── shortener.py      # Base62 encoding + link CRUD
│   │   │   └── analytics.py      # Click logging + daily aggregation upsert
│   │   └── routers/              # API route handlers
│   ├── Dockerfile                # Backend-only Docker build
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/           # Navbar, ShortenForm, ProtectedRoute
│   │   ├── pages/                # Home, Dashboard, Analytics, Login, Signup
│   │   ├── context/              # AuthContext (Supabase Auth)
│   │   └── lib/                  # API client (relative paths), Supabase client
│   └── package.json
└── supabase/
    └── migrations/
        └── 001_initial_schema.sql
```

---

## Local Development

### Prerequisites
- Python 3.11+, Node.js 18+, Redis, Supabase account (free)

### Setup

```bash
# 1. Clone
git clone https://github.com/Badri-2915/2goi.git
cd 2goi

# 2. Configure environment
cp backend/.env.example backend/.env   # Edit with your Supabase credentials
cp frontend/.env.example frontend/.env # Edit with your Supabase public keys

# 3. Run Supabase migration
# Go to Supabase SQL Editor -> run supabase/migrations/001_initial_schema.sql

# 4. Start Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 5. Start backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 6. Start frontend (separate terminal)
cd frontend
npm install && npm run dev
```

### Single-domain local test (optional)
```bash
cd frontend && npm run build
cp -r dist ../backend/static
# Now http://localhost:8000 serves everything
```

---

## API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/shorten` | Optional | Create short URL (Base62 from sequential ID) |
| GET | `/{short_code}` | No | 302 redirect (Redis -> DB fallback) |
| GET | `/api/links` | Required | List user's links (paginated) |
| GET | `/api/analytics/{short_code}` | Required | Click analytics (from daily_click_stats) |
| DELETE | `/api/links/{id}` | Required | Soft-delete a link |
| GET | `/api/health` | No | Health check (DB + Redis status) |

### Example: Shorten URL
```bash
curl -X POST https://2goi.in/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "custom_alias": "demo"}'
```
```json
{
  "short_url": "https://2goi.in/demo",
  "short_code": "demo",
  "original_url": "https://example.com",
  "qr_code": "iVBORw0KGgo...",
  "expires_at": null
}
```

---

## Production Deployment (Render)

1. Push repo to GitHub
2. Go to [render.com](https://render.com) -> **New +** -> **Blueprint**
3. Connect your repo -> Render reads `render.yaml`
4. Fill in secret environment variables (DB URL, Supabase keys)
5. Deploy -> get `https://2goi.onrender.com`
6. **Settings -> Custom Domains** -> add `2goi.in`
7. Add DNS records on GoDaddy as shown by Render
8. Configure Supabase Auth redirect URL: `https://2goi.in/**`

### Uptime Monitoring (UptimeRobot)

Render's free tier **sleeps the service after 15 minutes of inactivity**. The first request after sleep takes 30-60 seconds (cold start). To prevent this:

1. Create a free account at [uptimerobot.com](https://uptimerobot.com)
2. Add a new **HTTP(s)** monitor:
   - **URL:** `https://2goi.in/api/health`
   - **Interval:** 5 minutes
3. Save — UptimeRobot pings the health endpoint every 5 minutes, keeping the container warm 24/7

**Why UptimeRobot + Render?**
- Render hosts the app but puts it to sleep when idle (free tier limitation)
- UptimeRobot sends a real HTTP request every 5 minutes, preventing sleep
- Bonus: UptimeRobot emails you if the site goes down (free uptime alerts)

---

## Database Schema

```sql
links (id UUID PK, sequence_id BIGINT UNIQUE, original_url, short_code, user_id, click_count, is_active, created_at, expires_at)
clicks (id UUID PK, link_id FK, country, browser, device_type, referrer, ip_hash, clicked_at)
daily_click_stats (id UUID PK, link_id FK, date, click_count) -- UNIQUE(link_id, date)
users (id UUID PK, email, plan, created_at)
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [DOCUMENTATION.md](./DOCUMENTATION.md) | Complete project documentation — architecture, code, API, database, deployment |
| [SETUP_GUIDE.md](./SETUP_GUIDE.md) | Step-by-step setup guide — Supabase, Google OAuth, GoDaddy DNS, Render, Resend, Google Search Console, UptimeRobot |

---

## Monthly Cost

| Service | Cost |
|---------|------|
| Domain (2goi.in) | ~₹67/month |
| Render (web + Redis) | Free |
| Supabase (database + auth) | Free |
| Resend (emails) | Free (3,000/month) |
| Google Cloud (OAuth) | Free |
| UptimeRobot (uptime monitoring) | Free (50 monitors) |
| **Total** | **~₹67/month (domain only)** |
