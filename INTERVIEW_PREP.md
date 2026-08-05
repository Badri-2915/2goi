# 2GOI URL Shortener — Complete Interview Preparation Guide

> **Live:** https://2goi.in | **GitHub:** https://github.com/Badri-2915/2goi  
> Stack: FastAPI · React · PostgreSQL · Redis · Supabase · Docker · Render

---

# Table of Contents
1. Project Overview
2. System Architecture
3. Base62 Encoding
4. Database Design
5. Redis Caching
6. URL Shortening Workflow
7. Redirect Workflow
8. Click Analytics
9. Authentication & JWT
10. Error Handling
11. Security
12. Design Patterns
13. Tech Stack — What and Why
14. API Endpoints
15. Deployment — Docker & Render
16. Scalability
17. Challenges & Solutions
18. Project Folder Structure
19. Quick Interview Q&A
20. Monthly Cost

---
# 1. Project Overview

## 1.1 What Is 2GOI?

2GOI is a **production-grade URL shortening service** — same concept as Bitly or TinyURL — built from scratch and deployed at a real domain with real users.

**User flow:**
1. Visit https://2goi.in and paste a long URL like `https://amazon.in/dp/B0C6543WV8?ref=pd_aw`
2. Click "Shorten" → get back `https://2goi.in/2Bq` (3-character short link)
3. Also get a downloadable **QR code** for that short link
4. Anyone clicking `https://2goi.in/2Bq` is instantly redirected to the original URL

**Extra features for logged-in users:**
- Custom aliases (`2goi.in/myresume`)
- Click analytics — country, device, browser, daily trends
- Link expiration (auto-expire after N seconds)
- Soft delete (deactivate link, analytics preserved)
- Dashboard to manage all links

## 1.2 Why Did You Build This?

Demonstrates mastery of:
- Full-stack development (React + FastAPI)
- Database design (sequences, upsert, indexing, pre-aggregation)
- Caching (Redis cache-aside pattern)
- Authentication (JWT, OAuth, JWKS-based ES256 verification)
- Production deployment (Docker, custom domain, SSL, monitoring)
- System design (single-domain, horizontal scalability)
- Security (SQL injection, XSS, rate limiting, IP privacy)

## 1.3 Key Numbers

| Metric | Value |
|--------|-------|
| Short code length | 3–6 characters |
| Maximum unique codes | 62^6 = **56 billion** |
| Redirect speed (Redis hit) | **< 5ms** |
| Redirect speed (DB fallback) | ~20–50ms |
| Monthly cost | **~₹67 (domain only)** |
| Supabase free storage | 500 MB (~2–3M links) |
| Redis memory (free) | 25 MB |

## 1.4 Single-Domain Architecture

Everything on ONE domain (`2goi.in`). One Docker container serves React SPA + FastAPI API + short-code redirects. No `api.2goi.in`. No CORS issues in production. Fits in one free Render service.

---
# 2. System Architecture

## 2.1 Architecture Diagram

```
User → https://2goi.in (Render Docker Container)
         |
         FastAPI (Gunicorn + 4 async Uvicorn workers)
           |
           ├─ GET /             → React index.html (SPA homepage)
           ├─ GET /login        → React index.html (React Router handles)
           ├─ GET /assets/*     → JS/CSS bundles (StaticFiles)
           ├─ POST /api/shorten → Create short URL
           ├─ GET  /api/links   → User's links (auth required)
           ├─ DELETE /api/links/{id} → Soft-delete
           ├─ GET  /api/analytics/{code} → Click analytics
           ├─ GET/HEAD /api/health → DB + Redis status
           └─ GET /{short_code} → 302 Redirect  ← REGISTERED LAST
                    |
                    ├─ Redis.get("url:2Bq") → HIT: redirect <5ms
                    ├─ MISS → PostgreSQL → cache → redirect
                    └─ BackgroundTask: log click + upsert daily_stats
```

## 2.2 Infrastructure

```
Render.com
  ├── Docker Container (FastAPI + React build)
  └── Redis 25MB (free)
       └── connected via internal URL

Supabase
  ├── PostgreSQL 500MB (free)
  ├── Auth (JWT / Google OAuth)
  └── JWKS endpoint (ES256 public keys)

GoDaddy  → 2goi.in domain
UptimeRobot → pings /api/health every 5 min (prevents cold start)
Resend  → transactional emails (noreply@2goi.in)
```

## 2.3 Why Router Registration Order Matters

`GET /{short_code}` is a **catch-all** — matches any single-segment path. If registered first, it intercepts `/api/shorten`, `/login`, etc. Nothing else would work.

```python
# backend/app/main.py — ORDER IS CRITICAL
app.include_router(health.router)     # /api/health
app.include_router(shorten.router)    # /api/shorten
app.include_router(links.router)      # /api/links
app.include_router(analytics.router)  # /api/analytics/{code}
# static files served here
app.include_router(redirect.router)   # /{short_code}  ← ALWAYS LAST
```

Inside the redirect handler, reserved paths (`login`, `signup`, `dashboard`, `api*`) are explicitly skipped.

---
# 3. Base62 Encoding — How Short Codes Are Generated

## 3.1 What Is Base62?

Base62 uses 62 characters: `0-9` (10) + `a-z` (26) + `A-Z` (26) = **62 total**.  
Just like decimal uses 10 digits, Base62 uses 62 "digits" — representing large numbers in compact form.

## 3.2 Why Base62 Instead of Random Codes?

**Random approach (bad):**
```
1. Generate random "xYz1Q9"
2. SELECT * FROM links WHERE short_code = 'xYz1Q9'  ← extra DB query!
3. IF collision → retry from step 1
```
Problems: extra DB query every time; collision probability grows as DB fills.

**Base62 from sequential ID (our approach):**
```
1. INSERT row → PostgreSQL auto-generates sequence_id = 10005
2. short_code = encode_base62(10005) → "2Bl"
3. UPDATE row SET short_code = "2Bl"
→ ZERO collision checks. ZERO extra queries. Mathematically guaranteed unique.
```

Same approach used by **Bitly, TinyURL, and YouTube**.

## 3.3 The Algorithm

```python
BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode_base62(num: int) -> str:
    if num == 0:
        return BASE62_ALPHABET[0]
    encoded = []
    while num:
        num, rem = divmod(num, 62)
        encoded.append(BASE62_ALPHABET[rem])
    return "".join(reversed(encoded))
```

**Manual trace for sequence_id = 10000:**

| Step | num   | ÷62 quotient | remainder | character |
|------|-------|-------------|-----------|-----------|
| 1    | 10000 | 161         | 18        | `i`       |
| 2    | 161   | 2           | 37        | `B`       |
| 3    | 2     | 0           | 2         | `2`       |

Collected: `['i','B','2']` → reversed → **`"2Bi"`**

## 3.4 Why Start the Sequence at 10000?

- `encode_base62(1)` → `"1"` (1 char — too short)
- `encode_base62(10000)` → `"2Bi"` (3 chars — good minimum)

## 3.5 Capacity

| Code Length | Unique Codes | Notes |
|------------|-------------|-------|
| 3 chars | ~234K | Starting range |
| 4 chars | ~14.5M | |
| 5 chars | ~916M | |
| 6 chars | **~56 billion** | Enough for centuries |

At 1 million new links/day, 6-char codes last **155 years**.

---
# 4. Database Design

## 4.1 Four Tables

```
users             → registered user accounts
links             → every shortened URL (core table)
clicks            → raw click events (one row per click)
daily_click_stats → pre-aggregated click counts per day per link
```

## 4.2 Table: `links`

```sql
CREATE SEQUENCE link_id_seq START 10000;

CREATE TABLE links (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    sequence_id  BIGINT      UNIQUE NOT NULL DEFAULT nextval('link_id_seq'),
    original_url TEXT        NOT NULL,
    short_code   VARCHAR(20) UNIQUE NOT NULL,
    user_id      UUID        REFERENCES users(id),  -- NULL = anonymous
    click_count  INTEGER     NOT NULL DEFAULT 0,    -- denormalized for speed
    is_active    BOOLEAN     NOT NULL DEFAULT TRUE, -- soft delete flag
    created_at   TIMESTAMP   NOT NULL DEFAULT NOW(),
    expires_at   TIMESTAMP                          -- NULL = permanent
);
CREATE INDEX idx_links_short_code ON links(short_code);
CREATE INDEX idx_links_user_id    ON links(user_id);
```

| Column | Why It Exists |
|--------|--------------|
| `id` UUID | Safe external ID — not guessable |
| `sequence_id` BIGINT | Auto-increment → Base62 generation |
| `click_count` INTEGER | Denormalized total — avoids COUNT(*) query on dashboard |
| `is_active` BOOLEAN | Soft delete — false = deleted but row preserved |
| `expires_at` nullable | NULL = permanent; set = link dies at this time |

## 4.3 Table: `clicks`

```sql
CREATE TABLE clicks (
    id          UUID   PRIMARY KEY DEFAULT gen_random_uuid(),
    link_id     UUID   NOT NULL REFERENCES links(id) ON DELETE CASCADE,
    country     VARCHAR(10),
    browser     VARCHAR(50),
    device_type VARCHAR(20),
    referrer    VARCHAR(2048),
    ip_hash     VARCHAR(64),  -- SHA-256 of IP — raw IP NEVER stored
    clicked_at  TIMESTAMP NOT NULL DEFAULT NOW()
);
```

## 4.4 Table: `daily_click_stats` — Why It Exists

Without it, 30-day trend scans ALL click rows (millions). With it:

```sql
-- Always scans exactly 30 rows — fast regardless of click count
SELECT date, click_count FROM daily_click_stats
WHERE link_id = 'abc' ORDER BY date DESC LIMIT 30;
```

The `UNIQUE (link_id, date)` constraint enables the atomic upsert:

```sql
INSERT INTO daily_click_stats (link_id, date, click_count) VALUES (:id, TODAY, 1)
ON CONFLICT ON CONSTRAINT uq_daily_stats_link_date
DO UPDATE SET click_count = daily_click_stats.click_count + 1;
-- Atomic: no read-before-write race condition possible
```

## 4.5 Soft Delete vs Hard Delete

```sql
-- Hard delete (we do NOT use): destroys analytics history
DELETE FROM links WHERE id = 'abc';

-- Soft delete (our approach): analytics preserved
UPDATE links SET is_active = FALSE WHERE id = 'abc';
-- Redirect: WHERE is_active=TRUE → 404
-- Dashboard: WHERE is_active=TRUE → link not listed
-- Analytics: still accessible (is_active not checked here)
```

---
# 5. Redis Caching — Cache-Aside Pattern

## 5.1 Why Redis?

Without Redis: every redirect → PostgreSQL query (~20–50ms).  
With Redis: popular links served from memory in **< 5ms**.

## 5.2 Cache-Aside Pattern

```
Request: GET /2Bi
  1. Redis.get("url:2Bi")
     HIT  → return URL instantly (<5ms)
     MISS → continue
  2. PostgreSQL query
     Not found → 404
     Found → store in Redis → redirect
```

Only accessed links enter the cache (lazy). Cold links never waste memory.

## 5.3 Three Cache Operations

```python
# 1. Write-through on creation (new links cached immediately)
await redis.set(f"url:{link.short_code}", link.original_url)

# 2. Lazy load on miss (prime cache after DB query)
await redis.set(f"url:{short_code}", link.original_url)

# 3. Invalidation on deletion (prevent stale redirects)
await redis.delete(f"url:{short_code}")

# 4. TTL for expiring links (Redis auto-evicts — no cleanup job)
await redis.setex(f"url:{short_code}", ttl_seconds, link.original_url)
```

## 5.4 Redis Failure Handling

```python
try:
    cached_url = await redis.get(f"url:{short_code}")
except Exception:
    cached_url = None   # silent fallback to DB
# If Redis is down: redirects still work (~50ms). Users notice nothing.
```

**Redis is optional infrastructure** — app degrades gracefully, not catastrophically.

---
# 6. URL Shortening Workflow (Step by Step)

User submits `www.google.com`:

**Step 1 — Frontend auto-prepends https://**
```javascript
if (!/^https?:\/\//i.test(url)) url = "https://" + url;
```

**Step 2 — POST /api/shorten**
```json
{"url": "https://www.google.com", "custom_alias": null, "expires_in": null}
```

**Step 3 — Pydantic validates URL** (blocks `javascript:`, `data:`, non-http)

**Step 4 — Custom alias check** (if provided → SELECT → 409 if taken)

**Step 5 — DB INSERT triggers sequence**
```python
link = Link(original_url=url, short_code="__pending__", ...)
db.add(link)
await db.flush()   # PostgreSQL assigns sequence_id = 10005
```

**Step 6 — Base62 encode**
```python
link.short_code = encode_base62(10005)  # → "2Bl"
await db.commit()
```

**Step 7 — Prime Redis cache**
```python
await redis.set("url:2Bl", "https://www.google.com")
```

**Step 8 — Generate QR code**
```python
qr = qrcode.QRCode(version=1, box_size=10, border=4)
qr.add_data("https://2goi.in/2Bl")
qr.make(fit=True)
img = qr.make_image()
buffer = io.BytesIO()
img.save(buffer, format="PNG")
qr_base64 = base64.b64encode(buffer.getvalue()).decode()
```

**Step 9 — Return HTTP 201**
```json
{"short_url":"https://2goi.in/2Bl","short_code":"2Bl","qr_code":"iVBOR...","expires_at":null}
```

---
# 7. Redirect Workflow (Step by Step)

User clicks `https://2goi.in/2Bl`:

**Step 1** — Catch-all `GET /{short_code}` route receives request.

**Step 2 — Skip reserved paths**
```python
frontend_routes = {"login","signup","dashboard","analytics","favicon.svg"}
if short_code.startswith("api") or short_code in frontend_routes:
    raise HTTPException(404)  # → SPA fallback → React Router
```

**Step 3 — Redis check**
```python
try:
    cached_url = await redis.get(f"url:{short_code}")
except Exception:
    cached_url = None   # Redis down → fallback silently
```

**Step 4a — Cache HIT (< 5ms)**
```python
if cached_url:
    background_tasks.add_task(_log_click_background, ...)
    return RedirectResponse(url=cached_url, status_code=302)  # ← user is done
```

**Step 4b — Cache MISS**
```python
link = await get_link_by_code(db, short_code)
if not link: raise HTTPException(404, "Short URL not found")
if link.expires_at and link.expires_at < datetime.utcnow():
    raise HTTPException(410, "This link has expired")
await redis.set(f"url:{short_code}", link.original_url)
```

**Step 5 — Background task (AFTER response is sent)**
```python
async def _log_click_background(link_id, ip, ua, referrer):
    async with AsyncSessionLocal() as db:  # own session — request session already closed
        await log_click(db=db, ...)
        await increment_click_count(db, link_id)
```

## Why HTTP 302 (Not 301)?

| Code | Browser caches? | Effect |
|------|----------------|--------|
| 301 Permanent | Yes — forever | Delete/change link: browser ignores it — BAD |
| **302 Temporary** | **No** | Every click goes through our server — **CORRECT** |

---
# 8. Click Analytics System

## 8.1 What We Track Per Click

- **browser** — parsed from User-Agent (`user-agents` library)
- **device_type** — mobile/tablet/desktop
- **country** — from IP geolocation (or "Unknown")
- **referrer** — HTTP Referer header
- **ip_hash** — SHA-256(IP) — raw IP never stored

## 8.2 Click Logging Code

```python
async def log_click(db, link_id, ip_address, user_agent_string, referrer, country):
    ua          = parse_user_agent(user_agent_string)
    browser     = ua.browser.family
    device_type = "mobile" if ua.is_mobile else "tablet" if ua.is_tablet else "desktop"
    ip_hashed   = hashlib.sha256(ip_address.encode()).hexdigest()

    db.add(Click(link_id=link_id, country=country, browser=browser,
                 device_type=device_type, referrer=referrer, ip_hash=ip_hashed))

    # Atomic upsert — no race condition
    stmt = pg_insert(DailyClickStats).values(link_id=link_id, date=date.today(), click_count=1)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_daily_stats_link_date",
        set_={"click_count": DailyClickStats.click_count + 1}
    )
    await db.execute(stmt)
    await db.commit()
```

## 8.3 Analytics Queries (5 total)

```sql
-- Q1: Total clicks
SELECT COUNT(*) FROM clicks WHERE link_id = :id

-- Q2: Top countries
SELECT country, COUNT(*) FROM clicks WHERE link_id=:id GROUP BY country ORDER BY 2 DESC LIMIT 10

-- Q3: Devices
SELECT device_type, COUNT(*) FROM clicks WHERE link_id=:id GROUP BY device_type

-- Q4: Browsers
SELECT browser, COUNT(*) FROM clicks WHERE link_id=:id GROUP BY browser ORDER BY 2 DESC LIMIT 10

-- Q5: Daily trend (from pre-aggregated table — always O(days), not O(clicks))
SELECT date, click_count FROM daily_click_stats WHERE link_id=:id ORDER BY date DESC LIMIT 30
```

## 8.4 IP Extraction Behind Reverse Proxy

```python
def get_client_ip(request):
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()  # leftmost = real client
    return request.client.host
```

---
# 9. Authentication — Supabase Auth & JWT

## 9.1 Providers

- **Email + Password** — Supabase standard signup/login
- **Google OAuth** — one-click Google sign-in

## 9.2 JWT Verification (ES256 + HS256 Fallback)

```python
_jwks_client = PyJWKClient(f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json")
# Keys cached — not fetched on every request

async def verify_token(token):
    # Try ES256 via JWKS (modern Supabase — asymmetric)
    try:
        key = _jwks_client.get_signing_key_from_jwt(token)
        return pyjwt.decode(token, key.key, algorithms=["ES256"], audience="authenticated")
    except Exception:
        pass
    # Fallback: HS256 with shared secret (legacy — symmetric)
    return pyjwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated")
```

| Algorithm | Type | How Verified |
|-----------|------|-------------|
| ES256 | Asymmetric | Private key signs → public key (JWKS endpoint) verifies |
| HS256 | Symmetric | Same shared secret signs AND verifies |

## 9.3 JIT Provisioning

On first API call from a user, auto-create their DB record:

```python
if not user:
    user = User(id=UUID(user_id), email=payload["email"], plan="free")
    db.add(user); await db.commit()
# No signup webhook needed.
```

## 9.4 Duplicate Email Edge Case

Supabase returns fake success for existing emails (anti-enumeration). Detect it:

```javascript
if (data.user?.identities?.length === 0) {
    toast.error("Account already exists."); navigate("/login");
}
```

## 9.5 Dependency Injection

```python
# Optional auth (URL shortening works without login)
async def shorten_url(user: Optional[User] = Depends(get_current_user)):
    user_id = user.id if user else None

# Required auth (protected endpoints — auto-returns 401 if missing)
async def list_links(user: User = Depends(require_auth)):
    ...
```

---
# 10. Error Handling — Every Edge Case

## 10.1 Input Errors

| Scenario | Status | Detail |
|----------|--------|--------|
| Invalid URL (no http://) | 422 | Pydantic validator rejects |
| `javascript:alert(1)` | 422 | Regex blocks non-http protocols |
| Custom alias already taken | 409 | `{"detail": "Custom alias 'x' is already taken"}` |
| Empty URL | 422 | Required field |

## 10.2 Redirect Errors

| Scenario | Status |
|----------|--------|
| Short code not in DB | 404 Short URL not found |
| Link soft-deleted | 404 (WHERE is_active=TRUE filter) |
| Link expired | 410 This link has expired |
| Reserved path (login, api*) | 404 → SPA fallback → React Router |

## 10.3 System Errors

```python
# Redis down → silent fallback
try:
    cached_url = await redis.get(f"url:{short_code}")
except Exception:
    cached_url = None   # falls through to DB

# DB down → everything fails
# Health endpoint shows: {"status":"degraded","database":"error:..."}

# Render cold start → UptimeRobot pings /api/health every 5 min
```

## 10.4 Race Conditions — Concurrent Clicks

```python
# WRONG: read-modify-write (race condition)
count = SELECT click_count FROM links WHERE id='abc'  # both read 5
UPDATE links SET click_count = count + 1              # both write 6 → lost count

# RIGHT: atomic single statement
await db.execute(
    update(Link).where(Link.id == link_id)
                .values(click_count=Link.click_count + 1)
)
# Also for daily stats:
ON CONFLICT DO UPDATE SET click_count = click_count + 1
```

## 10.5 UptimeRobot 405 Bug (Fixed)

UptimeRobot sends `HEAD` by default → `@router.get()` returned 405 → false "site down" alerts.

```python
# Fix:
@router.api_route("/api/health", methods=["GET", "HEAD"])
```

---
# 11. Security Measures

## 11.1 SQL Injection Prevention

```python
# WRONG (string concatenation — injectable)
query = f"SELECT * FROM links WHERE short_code = '{short_code}'"

# RIGHT (SQLAlchemy ORM — always parameterized)
result = await db.execute(select(Link).where(Link.short_code == short_code))
# Sends:  SELECT * FROM links WHERE short_code = $1
# Param:  ['attacker_input']  — treated as string value, never as SQL
```

## 11.2 XSS Prevention

```python
@validator('url')
def validate_url(cls, v):
    if not re.match(r'^https?://', v, re.IGNORECASE):
        raise ValueError('URL must start with http:// or https://')
    return v
# Blocks: javascript:alert(1), data:text/html,..., vbscript:...
```

## 11.3 CSRF — Not Applicable

We use JWT Bearer tokens in the `Authorization` header — not cookies.  
Browsers do NOT auto-send `Authorization` headers cross-site.  
CSRF is only relevant for cookie-based auth. No CSRF token needed.

## 11.4 Rate Limiting (SlowAPI)

```python
limiter = Limiter(key_func=get_real_ip)
@limiter.limit("100/minute")   # anonymous
@limiter.limit("1000/minute")  # authenticated
# Exceeded → HTTP 429 Too Many Requests
```

## 11.5 IP Privacy

```python
ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()
# "203.0.113.42" → "a9b4c2d1..."  (one-way SHA-256 — irreversible)
# Raw IPs NEVER stored. Complies with GDPR data minimization.
```

## 11.6 Security Summary

| Threat | Mitigation |
|--------|-----------|
| SQL Injection | SQLAlchemy ORM (parameterized) |
| XSS | URL regex blocks `javascript:` / `data:` |
| CSRF | N/A — JWT Bearer tokens, not cookies |
| Brute force | SlowAPI: 100/min anon, 1000/min auth |
| IP tracking | SHA-256 hash; raw IP never stored |
| Token forgery | ES256/HS256 signature verification |
| Secret exposure | Env vars only; `.gitignore`; Render dashboard |
| MITM | HTTPS only (Let's Encrypt via Render) |

---
# 12. Design Patterns Used

| Pattern | Where | Problem Solved |
|---------|-------|---------------|
| **Cache-Aside** | Redis redirects | Fast reads; only cache what's accessed |
| **Write-Through** | Redis on creation | New links cached immediately |
| **Cache Invalidation** | Redis on deletion | No stale redirects |
| **Background Tasks** | Click logging | Analytics doesn't slow redirect |
| **Dependency Injection** | `Depends(get_db)`, `Depends(get_current_user)` | Clean, testable code |
| **Service Layer** | `services/shortener.py`, `services/analytics.py` | Business logic separate from HTTP |
| **Soft Delete** | `is_active=False` | Analytics preserved on deletion |
| **Upsert** | `daily_click_stats` | Atomic daily stat increment |
| **SPA Fallback** | 404 → `index.html` | React Router direct URLs work |
| **JIT Provisioning** | User auto-created first API call | No signup webhook |
| **Singleton** | `@lru_cache` on `get_settings()` | .env read once |
| **Catch-all Last** | `/{short_code}` registered last | API routes always win |

## Key Patterns in Detail

### Cache-Aside
App owns cache sync. Redis doesn't know about DB changes.  
Write to DB first, then write/delete from Redis. Reads check Redis first.

### Dependency Injection
```python
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session   # auto-closed after request (even on exception)

@router.post("/api/shorten")
async def shorten_url(
    db: AsyncSession = Depends(get_db),              # injected
    user: Optional[User] = Depends(get_current_user), # injected
):
    ...
```

### SPA Fallback
```python
@app.exception_handler(404)
async def spa_fallback(request, exc):
    if not request.url.path.startswith("/api"):
        return FileResponse(STATIC_DIR / "index.html")
    return JSONResponse(404, {"detail": "Not found"})
```

---
# 13. Tech Stack — What and Why

## 13.1 Backend

| Tech | Why |
|------|-----|
| **FastAPI** | Async Python, auto Swagger docs, Pydantic, DI built-in |
| **async SQLAlchemy** | Async ORM, parameterized queries, DB-agnostic |
| **Gunicorn + Uvicorn** | Multi-process (4 workers) + async ASGI |
| **SlowAPI** | Per-IP rate limiting, proxy-aware |
| **PyJWT + PyJWKClient** | ES256 JWKS + HS256 JWT verification |
| **user-agents** | Browser + device from User-Agent string |
| **qrcode** | QR PNG generation, Base64 encoded |
| **redis-py async** | Cache with TTL |

**Why FastAPI over Django?** Django is for full HTML apps (templates, admin, ORM). We need a REST API. FastAPI is purpose-built, async-native.  
**Why not Flask?** Flask is synchronous. Every DB/Redis call blocks. FastAPI handles thousands of concurrent requests with fewer threads.

## 13.2 Frontend

| Tech | Why |
|------|-----|
| **React 19 + Vite** | Vite is 10–100× faster than Webpack (native ESM) |
| **TailwindCSS** | Utility-first; no CSS files; purges unused styles |
| **Recharts** | React-native charts for analytics dashboard |
| **Supabase JS SDK** | Auth, token refresh, Google OAuth |
| **Axios** | API calls to FastAPI |

## 13.3 Infrastructure

| Tech | Why |
|------|-----|
| **PostgreSQL (Supabase)** | ACID, native sequences + upsert, full SQL |
| **Redis (Render)** | Sub-ms reads, built-in TTL, graceful fallback |
| **Docker multi-stage** | ~300MB image (no Node in prod vs ~1GB) |
| **Render** | Free tier, auto-deploy from GitHub |
| **Supabase** | Managed PG + Auth + JWKS + free |
| **UptimeRobot** | Free 5-min pings; prevents cold start |
| **Resend** | Transactional email, custom domain, 3K/month free |

---
# 14. API Endpoints Reference

| Method | Endpoint | Auth | Status | Description |
|--------|----------|------|--------|-------------|
| POST | `/api/shorten` | Optional | 201 | Create short URL + QR |
| GET | `/{short_code}` | None | 302 | Redirect to original |
| GET | `/api/links` | Required | 200 | List links (paginated) |
| DELETE | `/api/links/{id}` | Required | 204 | Soft-delete |
| GET | `/api/analytics/{code}` | Required | 200 | Click analytics |
| GET/HEAD | `/api/health` | None | 200 | DB + Redis status |

## POST `/api/shorten`

```json
// Request
{"url":"https://example.com","custom_alias":"demo","expires_in":86400}

// Response 201
{
  "short_url":    "https://2goi.in/demo",
  "short_code":   "demo",
  "original_url": "https://example.com",
  "qr_code":      "iVBORw0KGgo...",
  "expires_at":   "2026-04-04T12:00:00"
}
// Errors: 422 (invalid URL), 409 (alias taken)
```

## GET `/api/health`

```json
// Healthy
{"status":"healthy","database":"connected","redis":"connected"}

// Degraded
{"status":"degraded","database":"connected","redis":"error: Connection refused"}
```

## GET `/api/analytics/{code}`

```json
{
  "total_clicks": 1247,
  "countries":    [{"country":"IN","count":890}],
  "devices":      [{"device_type":"mobile","count":750}],
  "browsers":     [{"browser":"Chrome","count":680}],
  "daily_clicks": [{"date":"2026-03-01","count":120}]
}
```

---
# 15. Deployment — Docker & Render

## 15.1 Dockerfile — Multi-Stage Build

```dockerfile
# Stage 1: Build React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build        # Output: /app/frontend/dist/

# Stage 2: Python runtime (final image — no Node.js)
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
COPY --from=frontend-builder /app/frontend/dist ./static
CMD gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 --bind 0.0.0.0:$PORT --timeout 120
```

Final image ~300MB (not ~1GB). Node/node_modules only exist during build.

## 15.2 render.yaml

```yaml
services:
  - type: web
    name: twogoi-web
    runtime: docker
    healthCheckPath: /api/health
    envVars:
      - key: REDIS_URL
        fromService: {type: redis, name: twogoi-redis, property: connectionString}
      - key: DATABASE_URL
        sync: false   # set manually in Render dashboard
      - key: BASE_URL
        value: https://2goi.in
  - type: redis
    name: twogoi-redis
    plan: free
    maxmemoryPolicy: allkeys-lru
```

## 15.3 Custom Domain

```
1. [Render]  Add custom domain "2goi.in" → get CNAME target
2. [GoDaddy] Add CNAME: @ → twogoi.onrender.com
3. [Render]  Auto-provisions Let's Encrypt SSL
4. [Supabase] Auth → Site URL: https://2goi.in, Redirect: https://2goi.in/**
```

## 15.4 UptimeRobot Keep-Alive

Render free tier sleeps after 15 min inactivity (30–60s cold start).  
UptimeRobot pings `GET /api/health` every 5 minutes → container stays warm.  
**Bug fixed:** UptimeRobot uses `HEAD` → was getting 405.  
Fix: `@router.api_route("/api/health", methods=["GET","HEAD"])`

---
# 16. Scalability

## 16.1 Current Limits (Free Tier)

| Resource | Limit |
|----------|-------|
| Concurrent users | ~50–100 |
| Redirects/second | ~100–200 (Redis) / ~20–50 (DB) |
| Total links | ~2–3M (500MB Supabase) |
| Redis cached URLs | ~500K (25MB) |
| Monthly cost | ~₹67 (domain only) |

## 16.2 Scaling Phases

**Phase 1 — Thousands ($7–50/month)**  
Render paid tier → dedicated CPU. ~1K–5K concurrent users.

**Phase 2 — Tens of Thousands ($100–500/month)**
- Multiple FastAPI containers behind load balancer (**stateless → trivial horizontal scale**)
- Redis Cluster (1–5 GB) with LRU eviction
- PostgreSQL read replicas (analytics on replica, writes on primary)
- Cloudflare CDN (free) → edge-cache popular redirects globally

**Phase 3 — Hundreds of Thousands ($1K–5K/month)**
- Kubernetes with Horizontal Pod Autoscaler
- Click logging → Kafka → async workers
- Sharded PostgreSQL

**Phase 4 — Billions (Enterprise)**
- Cloudflare Workers handle redirects at edge — no origin server hit
- Multi-region PostgreSQL (CockroachDB or Citus)
- Analytics pipeline: Kafka → ClickHouse/BigQuery

## 16.3 Why FastAPI Scales With Zero Code Changes

App is completely **stateless** — all state in PostgreSQL + Redis.  
Start 1 or 100 containers — they behave identically.  
Load balancer uses round-robin. No sticky sessions.

## 16.4 Base62 Capacity at Scale

```
62^6 = 56,800,235,584 codes (~56 billion)
At 1 billion new links/day: codes last 56 days → just extend sequence
No schema changes needed — sequence is already BIGINT
```

---
# 17. Challenges Faced & Solutions

| # | Challenge | Solution |
|---|-----------|---------|
| 1 | Catch-all route intercepting everything | Register API routers first; skip reserved paths in handler |
| 2 | React Router direct URL → FastAPI 404 | Custom 404 handler → serve `index.html` (SPA fallback) |
| 3 | Supabase SSL connection errors | Use session pooler URL + `ssl_context` with `CERT_NONE` |
| 4 | ES256 vs HS256 JWT tokens | Try ES256 (JWKS) first, fall back to HS256 |
| 5 | Duplicate email signup silently accepted | Check `user.identities.length === 0` |
| 6 | Users type URLs without `https://` | Frontend auto-prepends protocol |
| 7 | UptimeRobot 405 on HEAD requests | `api_route(methods=["GET","HEAD"])` |
| 8 | Race condition on click count | Atomic `click_count = click_count + 1` SQL |
| 9 | Redis failures crashing redirects | Every Redis call in `try/except` with fallback |
| 10 | Slow analytics for popular links | Pre-aggregated `daily_click_stats` table |
| 11 | Background task using closed DB session | Task creates its own `AsyncSessionLocal()` session |

---
# 18. Project Folder Structure

```
2goi/
├── Dockerfile                      # Multi-stage: Node builds frontend → Python serves
├── render.yaml                     # Render Blueprint (web + Redis as code)
├── docker-compose.yml              # Local development
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py                 # FastAPI app, SPA serving, 404 fallback
│       ├── auth.py                 # JWT verification (ES256 JWKS + HS256 fallback)
│       ├── config.py               # Pydantic Settings + @lru_cache singleton
│       ├── database.py             # Async SQLAlchemy engine (Supabase SSL pooler)
│       ├── redis_client.py         # Async Redis client
│       ├── middleware.py           # SlowAPI rate limiter
│       ├── models/
│       │   ├── link.py             # Link model (sequence + Base62)
│       │   ├── click.py            # Click model
│       │   ├── daily_stats.py      # DailyClickStats model
│       │   └── user.py             # User model
│       ├── schemas/link.py         # Pydantic request/response + URL validator
│       ├── services/
│       │   ├── shortener.py        # Base62, create/get/delete links, QR code
│       │   └── analytics.py        # log_click, upsert, get_analytics
│       └── routers/
│           ├── health.py           # GET/HEAD /api/health
│           ├── shorten.py          # POST /api/shorten
│           ├── links.py            # GET /api/links, DELETE /api/links/{id}
│           ├── analytics.py        # GET /api/analytics/{code}
│           └── redirect.py         # GET /{short_code} — registered LAST
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Navbar.jsx
│       │   ├── ShortenForm.jsx     # Auto-prepends https://, shows QR
│       │   └── ProtectedRoute.jsx  # Auth guard
│       ├── pages/
│       │   ├── HomePage.jsx
│       │   ├── DashboardPage.jsx
│       │   ├── AnalyticsPage.jsx   # Recharts graphs
│       │   ├── LoginPage.jsx
│       │   └── SignupPage.jsx      # Detects duplicate emails
│       ├── context/AuthContext.jsx # Supabase auth state
│       └── lib/
│           ├── api.js              # Axios client (base URL config)
│           └── supabase.js         # Supabase client init
└── interview_prep/
    ├── s01_project_overview.py
    ├── s02_base62_encoding.py
    ├── s03_redis_caching.py
    ├── s04_database_design.py
    ├── s05_click_analytics.py
    ├── s06_auth_jwt.py
    ├── s07_error_handling.py
    ├── s08_security.py
    ├── s09_design_patterns.py
    ├── s10_tech_stack_why.py
    ├── s11_scalability.py
    └── s12_deployment_docker.py
```

---
# 19. Quick Interview Q&A

**Q: What is this project?**  
A: Production URL shortener at 2goi.in. Long URLs → short 3-char codes + QR codes. Click analytics (country/device/browser). React + FastAPI + PostgreSQL + Redis. Live with real users.

---

**Q: Why Base62 over random codes?**  
A: Random codes need a DB query to check collisions on every creation. Base62 from sequential IDs is mathematically guaranteed unique — zero extra queries, zero collisions. Same approach as Bitly and YouTube.

---

**Q: Why Redis? What if Redis goes down?**  
A: Sub-5ms redirects vs ~50ms without it. Every Redis call is in `try/except` — if Redis fails, app silently falls back to DB. Users notice nothing. Redis is optional infrastructure.

---

**Q: Why FastAPI over Django/Flask?**  
A: Django is for full HTML apps. Flask is synchronous (blocks on DB/Redis calls). FastAPI is async, auto-generates Swagger docs, has built-in Pydantic validation and dependency injection.

---

**Q: How do you handle security?**  
A: SQLAlchemy ORM (SQL injection), URL regex (XSS), JWT Bearer tokens (CSRF N/A), SlowAPI rate limiting, SHA-256 IP hashing, ES256/HS256 JWT verification, all secrets in env vars.

---

**Q: How do you handle concurrent clicks without losing counts?**  
A: Atomic SQL: `UPDATE links SET click_count = click_count + 1` — single statement, no read-before-write. Daily stats use `INSERT ON CONFLICT DO UPDATE SET click_count = click_count + 1`.

---

**Q: Why 302 redirect instead of 301?**  
A: 301 is cached by browsers forever. If we delete or change the link, browser ignores the change. 302 is never cached — every click goes through our server so changes take effect immediately.

---

**Q: Why pre-aggregate daily click stats?**  
A: Without it, analytics scans ALL click rows (O(total_clicks)). 1M clicks → slow. Pre-aggregation makes it O(days) — always 30 rows max, always fast.

---

**Q: How does JWT auth work?**  
A: Supabase issues JWTs. We verify with ES256 (JWKS public key) first, fall back to HS256 (shared secret). PyJWT checks signature + expiry. User UUID in `sub` claim → our `users` table. JIT provisioning: auto-create user on first API call.

---

**Q: What is the SPA fallback and why?**  
A: React Router handles navigation client-side. Direct visit to `2goi.in/dashboard` sends `GET /dashboard` to FastAPI — which has no such route → 404. Custom 404 handler: if path isn't `/api/*`, serve `index.html` → React loads → Router renders the right page.

---

**Q: How would you scale this?**  
A: FastAPI is stateless → multiple containers behind load balancer with zero code changes. Redis Cluster for distributed cache. PostgreSQL read replicas. Cloudflare edge redirects (CDN). Kafka for click event streaming at high scale.

---

**Q: What was the most interesting technical challenge?**  
A: The catch-all `GET /{short_code}` route intercepting all frontend routes (login, dashboard). Solved by registering API routers first, the redirect router last, and explicitly skipping reserved paths inside the handler. Also needed a 404 SPA fallback handler for React Router direct URL access.

---
# 20. Monthly Cost Breakdown

| Service | Cost |
|---------|------|
| GoDaddy domain (2goi.in) | ~₹67/month |
| Render Web Service | Free (512MB RAM, shared CPU) |
| Render Redis | Free (25MB) |
| Supabase PostgreSQL | Free (500MB, 50K MAU) |
| Supabase Auth | Free |
| Resend Email | Free (3,000 emails/month) |
| Google OAuth | Free |
| UptimeRobot | Free (50 monitors, 5-min intervals) |
| Cloudflare (optional) | Free (CDN + DDoS protection) |
| **TOTAL** | **~₹67/month (domain only!)** |

---

# 21. Key Code Snippets for Interview Reference

## Base62 Encode
```python
def encode_base62(num: int) -> str:
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if num == 0: return alphabet[0]
    encoded = []
    while num:
        num, rem = divmod(num, 62)
        encoded.append(alphabet[rem])
    return "".join(reversed(encoded))
```

## Cache-Aside Redirect
```python
cached = await redis.get(f"url:{code}")
if cached:
    return RedirectResponse(cached, 302)
link = await db.execute(select(Link).where(Link.short_code == code))
await redis.set(f"url:{code}", link.original_url)
return RedirectResponse(link.original_url, 302)
```

## Atomic Click Count
```python
await db.execute(
    update(Link).where(Link.id == link_id)
                .values(click_count=Link.click_count + 1)
)
```

## Upsert Daily Stats
```python
stmt = pg_insert(DailyClickStats).values(link_id=id, date=today, click_count=1)
stmt = stmt.on_conflict_do_update(
    constraint="uq_daily_stats_link_date",
    set_={"click_count": DailyClickStats.click_count + 1}
)
await db.execute(stmt)
```

## JWT Verification
```python
try:
    key = jwks_client.get_signing_key_from_jwt(token)
    return pyjwt.decode(token, key.key, algorithms=["ES256"], audience="authenticated")
except Exception:
    return pyjwt.decode(token, JWT_SECRET, algorithms=["HS256"], audience="authenticated")
```

## SPA Fallback
```python
@app.exception_handler(404)
async def spa_fallback(request, exc):
    if not request.url.path.startswith("/api"):
        return FileResponse(STATIC_DIR / "index.html")
    return JSONResponse(404, {"detail": "Not found"})
```

---

*End of 2GOI Interview Preparation Guide*
