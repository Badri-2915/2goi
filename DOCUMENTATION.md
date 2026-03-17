# 2GOI URL Shortener — Complete Project Documentation

## Table of Contents

1. [What is 2GOI?](#what-is-2goi)
2. [Live Demo](#live-demo)
3. [Tech Stack](#tech-stack)
4. [Architecture Overview](#architecture-overview)
5. [Project Structure](#project-structure)
6. [How Everything Works](#how-everything-works)
7. [Database Design](#database-design)
8. [API Reference](#api-reference)
9. [Frontend Pages](#frontend-pages)
10. [Authentication Flow](#authentication-flow)
11. [Caching Strategy](#caching-strategy)
12. [Base62 Short Code Generation](#base62-short-code-generation)
13. [Daily Click Aggregation](#daily-click-aggregation)
14. [Deployment](#deployment)
15. [Local Development Setup](#local-development-setup)
16. [Environment Variables](#environment-variables)
17. [File-by-File Explanation](#file-by-file-explanation)
18. [Sample Input/Output](#sample-inputoutput)
19. [Cost Breakdown](#cost-breakdown)
20. [Security](#security)

---

## What is 2GOI?

2GOI is a production-grade URL shortener that converts long URLs into short, shareable links. Think of it like Bitly or TinyURL, but built from scratch as a full-stack project.

**What it does:**
- Takes a long URL like `https://www.example.com/very/long/path?with=params`
- Converts it to a short link like `https://2goi.in/2Bi`
- When someone clicks the short link, they get redirected to the original URL
- Tracks every click with analytics (country, browser, device, daily trends)

**Key features:**
- Base62 short codes (deterministic, zero collisions)
- Redis-cached redirects (sub-5ms response time)
- Click analytics with charts (line, bar, pie charts)
- Custom aliases (e.g., `2goi.in/myresume`)
- Link expiration (auto-expire after X seconds)
- QR code generation for every link
- Google OAuth + email/password authentication
- Rate limiting to prevent abuse

---

## Live Demo

- **Website:** https://2goi.in
- **API Docs:** https://2goi.in/api/docs (Swagger UI)
- **Health Check:** https://2goi.in/api/health
- **GitHub:** https://github.com/Badri-2915/2goi

---

## Tech Stack

| Layer | Technology | Why we chose it |
|-------|-----------|----------------|
| **Frontend** | React 19 + Vite | Fast builds, modern React features |
| **Styling** | TailwindCSS | Utility-first CSS, fast to build UIs |
| **Icons** | Lucide React | Clean, consistent icon library |
| **Charts** | Recharts | Easy React chart library |
| **Backend** | FastAPI (Python) | Async, fast, auto-generates API docs |
| **ORM** | SQLAlchemy (async) | Type-safe database queries |
| **Database** | PostgreSQL (Supabase) | Reliable, free managed hosting |
| **Cache** | Redis | In-memory store for sub-5ms redirects |
| **Auth** | Supabase Auth | Handles signup, login, OAuth, JWT tokens |
| **Hosting** | Render | Free Docker deployment with custom domains |
| **Domain** | GoDaddy | Domain registration for 2goi.in |

---

## Architecture Overview

### Single-Domain Architecture

Everything runs on one domain (`2goi.in`) in a single Docker container:

```
                    https://2goi.in
                          |
                    +-----------+
                    |  FastAPI   |
                    |  Server    |
                    +-----------+
                   /    |    |    \
                  /     |    |     \
         /api/*   /assets  /{code}  /*other*
            |        |        |         |
        API Routes  Static  Redirect  SPA Fallback
        (JSON)     Files   (302)    (index.html)
            |        |        |
        Supabase   Vite     Redis
        PostgreSQL Build    Cache
                    Output
```

### Request Flow

1. **API requests** (`/api/*`) → Handled by FastAPI routers, return JSON
2. **Static assets** (`/assets/*`) → Served directly from the Vite build output
3. **Short URL redirects** (`/2Bi`) → Check Redis cache → Check DB → 302 redirect
4. **Frontend routes** (`/login`, `/dashboard`) → Serve `index.html` (React Router handles it)

---

## Project Structure

```
windsurf-project/
├── Dockerfile              # Multi-stage build (frontend + backend)
├── docker-compose.yml      # Local development setup
├── render.yaml             # Render deployment blueprint
├── README.md               # Quick start guide
├── DOCUMENTATION.md        # This file (detailed docs)
│
├── backend/                # Python FastAPI backend
│   ├── app/
│   │   ├── main.py         # App entry point, routes, SPA serving
│   │   ├── config.py       # Settings from environment variables
│   │   ├── database.py     # Async SQLAlchemy engine + sessions
│   │   ├── redis_client.py # Redis connection for caching
│   │   ├── auth.py         # JWT verification + user management
│   │   ├── middleware.py    # Rate limiting
│   │   │
│   │   ├── models/         # Database table definitions
│   │   │   ├── __init__.py # Registers all models
│   │   │   ├── link.py     # Links table (short URLs)
│   │   │   ├── click.py    # Clicks table (raw click events)
│   │   │   ├── user.py     # Users table (accounts)
│   │   │   └── daily_stats.py  # Daily click stats (pre-aggregated)
│   │   │
│   │   ├── schemas/        # Pydantic models (request/response shapes)
│   │   │   ├── link.py     # LinkCreate, ShortenResponse, LinkListResponse
│   │   │   └── click.py    # AnalyticsResponse, CountryBreakdown, etc.
│   │   │
│   │   ├── services/       # Business logic
│   │   │   ├── shortener.py    # Base62 encoding, link CRUD, QR codes
│   │   │   └── analytics.py    # Click logging, analytics queries
│   │   │
│   │   └── routers/        # API endpoint definitions
│   │       ├── shorten.py  # POST /api/shorten
│   │       ├── redirect.py # GET /{short_code}
│   │       ├── links.py    # GET /api/links, DELETE /api/links/{id}
│   │       ├── analytics.py    # GET /api/analytics/{short_code}
│   │       └── health.py   # GET /api/health
│   │
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Backend-only Dockerfile (for docker-compose)
│   └── .env                # Local environment variables (not in git)
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.jsx         # Root component with routing
│   │   ├── main.jsx        # Entry point (renders App)
│   │   │
│   │   ├── pages/          # Page components (one per route)
│   │   │   ├── HomePage.jsx      # Landing page with shortener form
│   │   │   ├── DashboardPage.jsx # User's links table
│   │   │   ├── AnalyticsPage.jsx # Click analytics with charts
│   │   │   ├── LoginPage.jsx     # Email/password + Google login
│   │   │   └── SignupPage.jsx    # Email/password + Google signup
│   │   │
│   │   ├── components/     # Reusable UI components
│   │   │   ├── Navbar.jsx        # Top navigation bar
│   │   │   ├── ShortenForm.jsx   # URL shortening form + QR display
│   │   │   └── ProtectedRoute.jsx # Auth guard for protected pages
│   │   │
│   │   ├── context/        # React context providers
│   │   │   └── AuthContext.jsx   # Authentication state management
│   │   │
│   │   └── lib/            # Utility libraries
│   │       ├── api.js      # Axios HTTP client for backend API
│   │       └── supabase.js # Supabase client initialization
│   │
│   ├── package.json        # Node.js dependencies
│   ├── vite.config.js      # Vite build configuration
│   ├── tailwind.config.js  # TailwindCSS configuration
│   └── .env                # Frontend env vars (not in git)
│
└── supabase/
    └── migrations/
        └── 001_initial_schema.sql  # Database schema (tables, indexes, RLS)
```

---

## How Everything Works

### 1. User Shortens a URL

```
User enters: https://www.google.com/search?q=hello+world

    Frontend (ShortenForm.jsx)
        |
        | POST /api/shorten { "url": "https://www.google.com/search?q=hello+world" }
        |
    Backend (shorten.py router)
        |
        | create_short_link() in shortener.py
        |
    Database
        | 1. INSERT INTO links (original_url, short_code="__pending__")
        | 2. PostgreSQL generates sequence_id = 10008
        | 3. Encode 10008 to Base62 = "2Bq"
        | 4. UPDATE short_code = "2Bq"
        |
    Redis
        | SET "url:2Bq" "https://www.google.com/search?q=hello+world"
        |
    QR Code
        | Generate QR code image → Base64 string
        |
    Response to Frontend:
        {
            "short_url": "https://2goi.in/2Bq",
            "short_code": "2Bq",
            "original_url": "https://www.google.com/search?q=hello+world",
            "qr_code": "iVBORw0KGgo...",  (Base64 PNG)
            "expires_at": null
        }
```

### 2. Someone Clicks the Short Link

```
Browser visits: https://2goi.in/2Bq

    FastAPI (redirect.py router)
        |
    Step 1: Check Redis Cache
        | GET "url:2Bq"
        | Cache HIT → "https://www.google.com/search?q=hello+world"
        |
    Step 2: Return Redirect
        | HTTP 302 → Location: https://www.google.com/search?q=hello+world
        |
    Step 3: Log Click (Background Task - doesn't slow down redirect)
        | Parse User-Agent → browser="Chrome", device="desktop"
        | Hash IP → "a1b2c3..." (SHA-256, no raw IPs stored)
        | INSERT INTO clicks (link_id, country, browser, device, ip_hash)
        | UPSERT daily_click_stats (link_id, today, click_count + 1)
        | UPDATE links SET click_count = click_count + 1

    Total time: ~3-5ms (cache hit) or ~20-50ms (cache miss + DB query)
```

### 3. User Views Analytics

```
User opens: https://2goi.in/analytics/2Bq

    Frontend (AnalyticsPage.jsx)
        |
        | GET /api/analytics/2Bq?days=30
        | Authorization: Bearer <JWT token>
        |
    Backend (analytics.py router)
        |
        | Verify JWT token (ES256 via JWKS)
        | Check user owns this link
        |
    Database Queries:
        | 1. SELECT count(*) FROM clicks WHERE link_id = ?      → total_clicks
        | 2. SELECT country, count(*) FROM clicks GROUP BY country → countries
        | 3. SELECT device_type, count(*) FROM clicks GROUP BY device → devices
        | 4. SELECT browser, count(*) FROM clicks GROUP BY browser → browsers
        | 5. SELECT date, click_count FROM daily_click_stats     → daily_clicks
        |    (This is the fast query from the pre-aggregated table!)
        |
    Response:
        {
            "short_code": "2Bq",
            "total_clicks": 42,
            "countries": [{"country": "US", "count": 20}, {"country": "IN", "count": 15}],
            "devices": [{"device_type": "mobile", "count": 25}, {"device_type": "desktop", "count": 17}],
            "browsers": [{"browser": "Chrome", "count": 30}, {"browser": "Safari", "count": 12}],
            "daily_clicks": [{"date": "2026-03-15", "count": 8}, {"date": "2026-03-16", "count": 12}]
        }
```

---

## Database Design

### Tables

#### 1. `links` — Shortened URLs

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key (safe to expose in APIs) |
| sequence_id | BIGINT | Auto-increment for Base62 encoding (starts at 10000) |
| original_url | TEXT | The long URL to redirect to |
| short_code | VARCHAR(20) | The short code (e.g., "2Bq" or "myresume") |
| user_id | UUID | Owner (nullable — anonymous links allowed) |
| click_count | INTEGER | Total clicks (denormalized for fast reads) |
| is_active | BOOLEAN | Soft delete flag |
| created_at | TIMESTAMP | When the link was created |
| expires_at | TIMESTAMP | Optional expiration time |

#### 2. `clicks` — Raw Click Events

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| link_id | UUID | Foreign key to links table |
| country | VARCHAR(10) | Visitor's country (e.g., "US") |
| browser | VARCHAR(50) | Browser name (e.g., "Chrome") |
| device_type | VARCHAR(20) | "mobile", "tablet", or "desktop" |
| referrer | VARCHAR(2048) | Where the click came from |
| ip_hash | VARCHAR(64) | SHA-256 hash of IP (privacy) |
| clicked_at | TIMESTAMP | When the click happened |

#### 3. `daily_click_stats` — Pre-Aggregated Daily Stats

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| link_id | UUID | Foreign key to links table |
| date | DATE | The calendar date |
| click_count | INTEGER | Total clicks for this link on this date |

**Unique constraint:** (link_id, date) — enables the upsert pattern

#### 4. `users` — User Accounts

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key (matches Supabase auth.users.id) |
| email | VARCHAR(255) | User's email |
| plan | VARCHAR(20) | "free" (for future premium tiers) |
| created_at | TIMESTAMP | When the user signed up |

### Relationships

```
users (1) ——→ (many) links (1) ——→ (many) clicks
                              (1) ——→ (many) daily_click_stats
```

---

## API Reference

### POST /api/shorten — Create a short link

**Request:**
```json
{
    "url": "https://www.google.com",
    "custom_alias": "mylink",
    "expires_in": 86400
}
```
- `url` (required): The long URL to shorten
- `custom_alias` (optional): Custom short code (3-20 chars, alphanumeric + hyphens)
- `expires_in` (optional): Seconds until link expires

**Response (201):**
```json
{
    "short_url": "https://2goi.in/mylink",
    "short_code": "mylink",
    "original_url": "https://www.google.com",
    "qr_code": "iVBORw0KGgo...",
    "expires_at": "2026-03-18T09:00:00"
}
```

### GET /{short_code} — Redirect

**Response:** HTTP 302 redirect to the original URL

**Error responses:**
- 404: Short code not found
- 410: Link has expired

### GET /api/links — List user's links (requires auth)

**Query params:** `page=1`, `page_size=20`, `sort_by=created_at|click_count|expires_at`

**Response:**
```json
{
    "links": [
        {
            "id": "uuid-here",
            "original_url": "https://www.google.com",
            "short_code": "2Bq",
            "short_url": "https://2goi.in/2Bq",
            "click_count": 42,
            "is_active": true,
            "created_at": "2026-03-17T09:00:00",
            "expires_at": null
        }
    ],
    "total": 15,
    "page": 1,
    "page_size": 20
}
```

### DELETE /api/links/{link_id} — Delete a link (requires auth)

**Response:** 204 No Content (also removes from Redis cache)

### GET /api/analytics/{short_code} — Get analytics (requires auth)

**Query params:** `days=30` (1-365)

**Response:**
```json
{
    "short_code": "2Bq",
    "total_clicks": 42,
    "countries": [{"country": "US", "count": 20}],
    "devices": [{"device_type": "mobile", "count": 25}],
    "browsers": [{"browser": "Chrome", "count": 30}],
    "daily_clicks": [{"date": "2026-03-17", "count": 15}]
}
```

### GET /api/health — Health check

**Response:**
```json
{
    "status": "healthy",
    "database": "connected",
    "redis": "connected"
}
```

---

## Frontend Pages

| Page | Route | Auth Required | Description |
|------|-------|---------------|-------------|
| **Home** | `/` | No | Landing page with URL shortener form and feature cards |
| **Login** | `/login` | No | Email/password login + Google OAuth button |
| **Signup** | `/signup` | No | Account creation + Google OAuth button |
| **Dashboard** | `/dashboard` | Yes | Table of user's links with copy, analytics, delete actions |
| **Analytics** | `/analytics/:code` | Yes | Charts showing click trends, countries, devices, browsers |

---

## Authentication Flow

### How Login Works

```
1. User clicks "Sign In" or "Continue with Google"

2. Frontend calls Supabase Auth:
   - Email/password: supabase.auth.signInWithPassword()
   - Google: supabase.auth.signInWithOAuth() → redirects to Google

3. Supabase returns a JWT token (stored in localStorage by Supabase JS)

4. On every API request, the Axios interceptor:
   - Gets the current session from Supabase
   - Attaches the JWT as: Authorization: Bearer <token>

5. Backend receives the request:
   - Extracts the JWT from the Authorization header
   - Verifies it using Supabase's JWKS endpoint (ES256 algorithm)
   - Extracts user_id from the "sub" claim
   - Looks up or creates the user in our database
   - Passes the User object to the route handler
```

### Token Verification (Backend)

The backend supports two JWT algorithms:
1. **ES256** (primary): Uses Supabase's public keys from the JWKS endpoint
2. **HS256** (fallback): Uses the JWT secret for legacy tokens

---

## Caching Strategy

### Cache-Aside Pattern (Lazy Loading)

```
Redirect Request (GET /2Bq)
    |
    v
Check Redis: GET "url:2Bq"
    |
    ├── Cache HIT → Return cached URL (3-5ms)
    |
    └── Cache MISS → Query PostgreSQL → Store in Redis → Return URL (20-50ms)
```

### Cache Operations

| Event | Redis Action |
|-------|-------------|
| Link created | `SET "url:{code}" "{original_url}"` (prime cache) |
| Link clicked (cache miss) | `SET "url:{code}" "{original_url}"` (fill cache) |
| Link deleted | `DEL "url:{code}"` (invalidate cache) |
| Link with TTL | `SETEX "url:{code}" {ttl} "{original_url}"` (auto-expire) |

### Redis Failure Handling

Redis is optional. All Redis operations are wrapped in try/except blocks. If Redis goes down, the app falls back to database queries (slower but still works).

---

## Base62 Short Code Generation

### What is Base62?

Base62 uses 62 characters: `0-9`, `a-z`, `A-Z`

It converts a number into a short string, similar to how Base10 uses 0-9.

### How it works

```
Number:    10000
Base62:    "2Bi"

Encoding process:
  10000 ÷ 62 = 161 remainder 18  → 18 = 'i'
  161   ÷ 62 = 2   remainder 37  → 37 = 'B'
  2     ÷ 62 = 0   remainder 2   → 2  = '2'

  Read backwards: "2Bi"
```

### Why Base62 over random codes?

| Approach | Collision Risk | Extra DB Queries | Used By |
|----------|---------------|------------------|---------|
| **Random codes** | High (must check for duplicates) | 1-3 per link | Simple apps |
| **Base62 from sequential ID** | Zero (each ID is unique) | 0 | Bitly, TinyURL, YouTube |

### Code capacity

| Characters | Unique Codes | Example |
|------------|-------------|---------|
| 3 chars | 238,328 | "2Bi" |
| 4 chars | 14,776,336 | "2Biq" |
| 5 chars | 916,132,832 | "2Biq7" |
| 6 chars | 56+ billion | "2Biq7X" |

The sequence starts at 10000 (guarantees minimum 3 characters).

---

## Daily Click Aggregation

### The Problem

Without aggregation, getting "clicks per day for the last 30 days" requires scanning ALL click rows:

```sql
-- SLOW: Scans every click row (O(total_clicks))
SELECT DATE(clicked_at), COUNT(*) FROM clicks
WHERE link_id = ? GROUP BY DATE(clicked_at)
ORDER BY DATE(clicked_at) LIMIT 30;
```

If a link has 100,000 clicks, this scans 100,000 rows just to get 30 numbers.

### The Solution

Maintain a pre-aggregated table that stores one row per link per day:

```sql
-- FAST: Only reads 30 rows (O(days))
SELECT date, click_count FROM daily_click_stats
WHERE link_id = ? ORDER BY date DESC LIMIT 30;
```

### How the upsert works

On every click, we run this PostgreSQL query:

```sql
INSERT INTO daily_click_stats (link_id, date, click_count)
VALUES ('uuid', '2026-03-17', 1)
ON CONFLICT (link_id, date)
DO UPDATE SET click_count = daily_click_stats.click_count + 1;
```

- **First click of the day:** Creates a new row with `click_count = 1`
- **Subsequent clicks:** Increments `click_count` by 1

This is called an "upsert" (UPDATE + INSERT) and it's a single atomic SQL statement.

---

## Deployment

### Production Setup (Render)

```
GitHub Push
    |
    v
Render (auto-deploy)
    |
    ├── Builds Docker image (multi-stage)
    │   ├── Stage 1: npm ci + npm run build (React)
    │   └── Stage 2: pip install + copy backend + copy frontend dist
    |
    ├── Starts Gunicorn with 4 Uvicorn workers
    |
    └── Connected to:
        ├── Supabase PostgreSQL (ap-south-1)
        ├── Render Redis (same region)
        └── Custom domain: 2goi.in
```

### DNS Configuration (GoDaddy)

| Type | Name | Value |
|------|------|-------|
| A | @ | 216.24.57.1 |
| CNAME | www | twogoi.onrender.com |

---

## Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Redis (via Docker or local install)

### Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Badri-2915/2goi.git
cd 2goi

# 2. Set up backend
cd backend
python -m venv venv
source venv/bin/activate          # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Edit with your Supabase credentials

# 3. Start Redis (in a separate terminal)
docker run -p 6379:6379 redis:7-alpine

# 4. Start backend (in backend/ directory)
uvicorn app.main:app --reload --port 8000

# 5. Set up frontend (in a separate terminal)
cd frontend
npm install
cp .env.example .env              # Edit with your Supabase public keys

# 6. Start frontend
npm run dev                        # Opens at http://localhost:5173
```

### Or use Docker Compose

```bash
docker-compose up                  # Starts backend + Redis
cd frontend && npm run dev         # Start frontend separately
```

---

## Environment Variables

### Backend (.env)

| Variable | Description | Example |
|----------|------------|---------|
| `DATABASE_URL` | Async PostgreSQL URL | `postgresql+asyncpg://user:pass@host:5432/db` |
| `DATABASE_URL_SYNC` | Sync PostgreSQL URL | `postgresql://user:pass@host:5432/db` |
| `SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Admin key (SECRET) | `eyJ...` |
| `SUPABASE_ANON_KEY` | Public key | `eyJ...` |
| `SUPABASE_JWT_SECRET` | JWT secret | `your-jwt-secret` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `BASE_URL` | Short link domain | `https://2goi.in` |
| `ENVIRONMENT` | development/production | `production` |

### Frontend (.env)

| Variable | Description | Example |
|----------|------------|---------|
| `VITE_API_URL` | Backend API URL (empty = same domain) | `` |
| `VITE_SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Supabase public key | `eyJ...` |

---

## File-by-File Explanation

### Backend Files

| File | What it does |
|------|-------------|
| `main.py` | Creates the FastAPI app, registers routers, serves React SPA, handles 404 fallback |
| `config.py` | Loads all settings from .env file using Pydantic BaseSettings |
| `database.py` | Sets up async SQLAlchemy engine with connection pooling and SSL for Supabase |
| `redis_client.py` | Creates async Redis client for caching short link redirects |
| `auth.py` | Verifies Supabase JWT tokens (ES256 via JWKS), auto-creates users on first login |
| `middleware.py` | Rate limiting using SlowAPI (100 req/min anon, 1000 req/min auth) |
| `models/link.py` | Link table: UUID primary key, sequence_id for Base62, original_url, short_code, etc. |
| `models/click.py` | Click table: stores each click with browser, device, country, hashed IP |
| `models/user.py` | User table: synced from Supabase Auth, stores email and plan |
| `models/daily_stats.py` | Daily stats table: pre-aggregated click counts per link per day |
| `services/shortener.py` | Base62 encoding, link creation (insert → flush → encode), QR generation, pagination |
| `services/analytics.py` | Click logging with daily upsert, analytics queries with breakdowns |
| `routers/shorten.py` | POST /api/shorten — creates link, primes Redis cache, returns QR code |
| `routers/redirect.py` | GET /{code} — Redis check → DB fallback → 302 redirect + async click logging |
| `routers/links.py` | GET /api/links (paginated list), DELETE /api/links/{id} (soft delete + cache invalidation) |
| `routers/analytics.py` | GET /api/analytics/{code} — returns total clicks, country/device/browser/daily breakdowns |
| `routers/health.py` | GET /api/health — checks database and Redis connectivity |
| `schemas/link.py` | Pydantic models for link creation, response, and list response with validation |
| `schemas/click.py` | Pydantic models for analytics response with all breakdown types |

### Frontend Files

| File | What it does |
|------|-------------|
| `App.jsx` | Root component: sets up routing, auth provider, navbar, toast notifications |
| `lib/supabase.js` | Initializes Supabase JS client with project URL and anon key |
| `lib/api.js` | Axios HTTP client with JWT interceptor, exports API helper functions |
| `context/AuthContext.jsx` | React context for auth state: user, session, signUp, signIn, signOut |
| `components/Navbar.jsx` | Top nav: shows Home + Sign In (guest) or Home + Dashboard + Sign Out (user) |
| `components/ShortenForm.jsx` | URL input + advanced options + result display with QR code and copy button |
| `components/ProtectedRoute.jsx` | Auth guard: shows spinner while loading, redirects to /login if not authenticated |
| `pages/HomePage.jsx` | Landing page: hero section with shortener form + 6 feature cards + footer |
| `pages/DashboardPage.jsx` | Link table with sort, copy, analytics, delete, and pagination |
| `pages/AnalyticsPage.jsx` | Charts: line (daily trend), bar (countries), pie (devices), progress bars (browsers) |
| `pages/LoginPage.jsx` | Email/password form + Google OAuth button + link to signup |
| `pages/SignupPage.jsx` | Email/password form with confirmation + Google OAuth + link to login |

### Infrastructure Files

| File | What it does |
|------|-------------|
| `Dockerfile` | Multi-stage: Stage 1 builds React, Stage 2 sets up Python + copies built frontend |
| `render.yaml` | Render blueprint: defines web service (Docker) + Redis service with all env vars |
| `docker-compose.yml` | Local dev: starts backend (with hot-reload) + Redis |
| `.gitignore` | Excludes .env, node_modules, venv, build artifacts from Git |

---

## Sample Input/Output

### 1. Shorten a URL (anonymous)

**Request:**
```bash
curl -X POST https://2goi.in/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/Badri-2915/2goi"}'
```

**Response:**
```json
{
    "short_url": "https://2goi.in/2Bi",
    "short_code": "2Bi",
    "original_url": "https://github.com/Badri-2915/2goi",
    "qr_code": "iVBORw0KGgoAAAANSUhEUg...",
    "expires_at": null
}
```

### 2. Shorten with custom alias (authenticated)

**Request:**
```bash
curl -X POST https://2goi.in/api/shorten \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
  -d '{"url": "https://linkedin.com/in/badri", "custom_alias": "myresume"}'
```

**Response:**
```json
{
    "short_url": "https://2goi.in/myresume",
    "short_code": "myresume",
    "original_url": "https://linkedin.com/in/badri",
    "qr_code": "iVBORw0KGgoAAAANSUhEUg...",
    "expires_at": null
}
```

### 3. Click the short link

```bash
curl -v https://2goi.in/2Bi
# < HTTP/2 302
# < location: https://github.com/Badri-2915/2goi
```

### 4. Health check

```bash
curl https://2goi.in/api/health
```
```json
{
    "status": "healthy",
    "database": "connected",
    "redis": "connected"
}
```

---

## Cost Breakdown

| Service | Cost | Duration |
|---------|------|----------|
| Render Web (free tier) | $0/month | Forever |
| Render Redis (free tier) | $0/month | Forever |
| Supabase DB + Auth (free tier) | $0/month | Forever |
| GoDaddy domain (2goi.in) | ~$8/year | Yearly renewal |
| **Total** | **~$0.67/month** | |

---

## Security

### What's protected

- **Service role key**: Only on the backend, never exposed to frontend
- **JWT secret**: Only on the backend, used for HS256 fallback
- **Database password**: Only in Render environment variables
- **IP addresses**: Hashed with SHA-256 before storage (no raw IPs)
- **Protected routes**: Dashboard and Analytics require JWT authentication
- **Rate limiting**: 100 req/min (anonymous), 1000 req/min (authenticated)

### What's public (by design)

- **Supabase URL**: Public project identifier
- **Supabase anon key**: Public key designed for frontend use (only allows RLS-restricted access)
- **Short codes**: Anyone with the short URL can access the redirect

### Auth Security

- JWT tokens verified using Supabase's JWKS endpoint (ES256 public keys)
- Tokens expire automatically (managed by Supabase)
- Users can only view/delete their own links
- Google OAuth configured with restricted callback URLs

---

*Built by Badri Pamisetty — https://github.com/Badri-2915/2goi*
