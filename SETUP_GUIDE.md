# 2GOI URL Shortener — Complete Setup & Configuration Guide

This guide walks you through setting up every external service needed to deploy 2GOI from scratch. Follow the sections in order.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Supabase Setup (Database + Auth)](#2-supabase-setup-database--auth)
3. [Google Cloud Console (OAuth)](#3-google-cloud-console-oauth)
4. [GoDaddy Domain & DNS](#4-godaddy-domain--dns)
5. [Render Deployment (Hosting)](#5-render-deployment-hosting)
6. [Resend (Email Service)](#6-resend-email-service)
7. [Google Search Console (SEO)](#7-google-search-console-seo)
8. [UptimeRobot (Uptime Monitoring)](#8-uptimerobot-uptime-monitoring)
9. [Environment Variables Reference](#9-environment-variables-reference)
10. [Verification Checklist](#10-verification-checklist)

---

## 1. Prerequisites

Before starting, ensure you have:

- **GitHub account** with a repository for the project
- **Node.js 20+** and **Python 3.11+** installed locally
- **A domain name** (e.g., `2goi.in` from GoDaddy)
- **Credit/Debit card** — NOT required (all services have free tiers)

### Accounts to create (all free):

| Service | URL | Purpose |
|---------|-----|---------|
| Supabase | https://supabase.com | Database + Authentication |
| Google Cloud Console | https://console.cloud.google.com | Google OAuth (Login with Google) |
| GoDaddy | https://godaddy.com | Domain registration & DNS |
| Render | https://render.com | Web hosting (Docker) + Redis |
| Resend | https://resend.com | Transactional emails (confirmations) |
| Google Search Console | https://search.google.com/search-console | SEO indexing |

---

## 2. Supabase Setup (Database + Auth)

Supabase provides the PostgreSQL database and authentication (email/password + Google OAuth).

### Step 2.1: Create a Supabase Project

1. Go to **https://supabase.com/dashboard**
2. Click **"New Project"**
3. Fill in:
   - **Name:** `2goi` (or any name)
   - **Database Password:** Choose a strong password — **save this, you'll need it later**
   - **Region:** Choose the closest to your users (e.g., `South Asia (Mumbai)` → `aws-ap-south-1`)
4. Click **"Create new project"** — wait ~2 minutes for setup

### Step 2.2: Get Your Project Credentials

After the project is created, go to **Project Settings** (gear icon, bottom-left) → **API**:

| Credential | Where to find | Used for |
|------------|--------------|----------|
| **Project URL** | Settings → API → Project URL | `SUPABASE_URL` and `VITE_SUPABASE_URL` |
| **anon (public) key** | Settings → API → Project API keys → `anon` | `SUPABASE_ANON_KEY` and `VITE_SUPABASE_ANON_KEY` |
| **service_role key** | Settings → API → Project API keys → `service_role` | `SUPABASE_SERVICE_ROLE_KEY` (backend only, NEVER expose) |
| **JWT Secret** | Settings → API → JWT Settings → JWT Secret | `SUPABASE_JWT_SECRET` |

### Step 2.3: Get Database Connection Strings

Go to **Project Settings** → **Database** → **Connection string**:

1. Select **Session pooler** mode (required — Supabase is IPv6-only, pooler provides IPv4 access)
2. Select **URI** format
3. Copy the connection string. It looks like:
   ```
   postgresql://postgres.XXXXX:[YOUR-PASSWORD]@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
   ```

You need **two versions** of this string:

| Variable | Format | Driver |
|----------|--------|--------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres.XXXXX:PASSWORD@aws-1-REGION.pooler.supabase.com:5432/postgres` | asyncpg (async) |
| `DATABASE_URL_SYNC` | `postgresql://postgres.XXXXX:PASSWORD@aws-1-REGION.pooler.supabase.com:5432/postgres` | psycopg2 (sync) |

> **Important:** Replace `[YOUR-PASSWORD]` with your actual database password from Step 2.1.

### Step 2.4: Create Database Tables

Go to **SQL Editor** in Supabase Dashboard and run the schema file:

```sql
-- Copy the contents of supabase/migrations/001_initial_schema.sql and run it here
```

Alternatively, the backend auto-creates tables on startup via SQLAlchemy's `Base.metadata.create_all()`.

### Step 2.5: Configure Authentication

1. Go to **Authentication** → **Providers** → **Email**
2. Settings:
   - **Enable Email provider:** ON
   - **Confirm email:** ON (turn ON after setting up Resend SMTP — see Section 6)
   - **Secure email change:** ON
3. Go to **Authentication** → **URL Configuration**
4. Set:
   - **Site URL:** `https://2goi.in`
   - **Redirect URLs:** Add `https://2goi.in/dashboard`

### Step 2.6: Enable Google OAuth in Supabase

1. Go to **Authentication** → **Providers** → **Google**
2. Toggle **Enable Google provider** → ON
3. You'll see fields for:
   - **Client ID** — get this from Google Cloud Console (Section 3)
   - **Client Secret** — get this from Google Cloud Console (Section 3)
4. Copy the **Callback URL** shown by Supabase (looks like `https://XXXXX.supabase.co/auth/v1/callback`) — you'll need this in Google Cloud Console

---

## 3. Google Cloud Console (OAuth)

This section sets up "Login with Google" functionality.

### Step 3.1: Create a Google Cloud Project

1. Go to **https://console.cloud.google.com**
2. Click the project dropdown (top-left) → **"New Project"**
3. Name: `2GOI URL Shortener`
4. Click **"Create"**
5. Select the new project from the dropdown

### Step 3.2: Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen** (left sidebar)
2. Select **"External"** user type → click **"Create"**
3. Fill in the consent screen:
   - **App name:** `2GOI URL Shortener`
   - **User support email:** Your email
   - **App logo:** Optional (upload your logo)
   - **App domain:**
     - Application home page: `https://2goi.in`
     - Application privacy policy: `https://2goi.in` (or leave blank for now)
     - Application terms of service: `https://2goi.in` (or leave blank for now)
   - **Authorized domains:** Add `2goi.in` and `supabase.co`
   - **Developer contact email:** Your email
4. Click **"Save and Continue"**
5. **Scopes:** Click "Add or Remove Scopes" → select:
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
   - `openid`
6. Click **"Save and Continue"**
7. **Test users:** Skip (not needed for External type)
8. Click **"Back to Dashboard"**

### Step 3.3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials** (left sidebar)
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. Fill in:
   - **Application type:** Web application
   - **Name:** `2GOI Web Client`
   - **Authorized JavaScript origins:** Add:
     - `https://2goi.in`
     - `https://XXXXX.supabase.co` (your Supabase project URL)
   - **Authorized redirect URIs:** Add:
     - `https://XXXXX.supabase.co/auth/v1/callback` (the callback URL from Supabase Step 2.6)
4. Click **"Create"**
5. A dialog appears with:
   - **Client ID:** `1234567890-xxxxx.apps.googleusercontent.com`
   - **Client Secret:** `GOCSPX-xxxxx`
6. **Copy both values** — you need them for Supabase

### Step 3.4: Add Credentials to Supabase

1. Go back to **Supabase Dashboard** → **Authentication** → **Providers** → **Google**
2. Paste:
   - **Client ID:** from Step 3.3
   - **Client Secret:** from Step 3.3
3. Click **Save**

### Step 3.5: Publish the OAuth App (Important!)

By default, your OAuth app is in **"Testing"** mode, which limits login to 100 test users.

1. Go to **OAuth consent screen** in Google Cloud Console
2. Click **"PUBLISH APP"**
3. Confirm the dialog

> **Note:** Google may show a warning that "This app isn't verified." This is normal for new apps. Users will see a "Continue" button to proceed. To remove the warning, you'd need to go through Google's verification process (optional, requires privacy policy page).

---

## 4. GoDaddy Domain & DNS

### Step 4.1: Register a Domain

1. Go to **https://godaddy.com**
2. Search for your desired domain (e.g., `2goi.in`)
3. Purchase it (~$8/year for `.in` domains)

### Step 4.2: Configure DNS Records

Go to **GoDaddy** → **My Products** → Your domain → **DNS** → **Manage DNS**

Add/modify these records:

#### Required: Point domain to Render

| Type | Name | Value | TTL |
|------|------|-------|-----|
| **A** | `@` | `216.24.57.1` | 1/2 Hour |
| **CNAME** | `www` | `twogoi.onrender.com` | 1/2 Hour |

> **Note:** The A record IP `216.24.57.1` is Render's load balancer IP. The CNAME redirects `www.2goi.in` to your Render service.

#### Required: Google Search Console verification (if using DNS method)

| Type | Name | Value | TTL |
|------|------|-------|-----|
| **TXT** | `@` | `google-site-verification=XXXXX` (from Google Search Console) | 1/2 Hour |

#### Required: Resend email verification (3 records)

These are added automatically if you use GoDaddy's auto-configure with Resend (see Section 6). If adding manually:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| **TXT** | `resend._domainkey` | `p=MIGfMA0GCSqG...` (full DKIM key from Resend) | 1/2 Hour |
| **MX** | `send` | `feedback-smtp.us-east-1.amazonses.com` (Priority: 10) | 1/2 Hour |
| **TXT** | `send` | `v=spf1 include:amazonses.com ~all` | 1/2 Hour |

#### Summary: All DNS records when fully configured

| Type | Name | Value | Purpose |
|------|------|-------|---------|
| A | @ | 216.24.57.1 | Render hosting |
| CNAME | www | twogoi.onrender.com | www redirect |
| TXT | @ | google-site-verification=XXXXX | Google Search Console |
| TXT | resend._domainkey | p=MIGfMA0GCSqG... | Resend DKIM |
| MX | send | feedback-smtp.[...].amazonses.com | Resend sending |
| TXT | send | v=spf1 include:amazonses.com ~all | Resend SPF |

---

## 5. Render Deployment (Hosting)

Render hosts the Docker container (FastAPI + React) and Redis cache.

### Step 5.1: Connect GitHub Repository

1. Go to **https://dashboard.render.com**
2. Sign in with GitHub
3. Click **"New +"** → **"Blueprint"**
4. Connect your GitHub repo (`Badri-2915/2goi`)
5. Render reads `render.yaml` and creates:
   - **Web service:** `2goi` (Docker, free tier)
   - **Redis service:** `2goi-redis` (free tier)

### Step 5.2: Set Environment Variables

After the Blueprint creates the services, go to the **web service** (`2goi`) → **Environment**:

Set the following **secret** variables (these have `sync: false` in render.yaml):

| Variable | Value | Where to get it |
|----------|-------|-----------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres.XXXXX:PASS@aws-1-REGION.pooler.supabase.com:5432/postgres` | Supabase → Settings → Database → Connection string (Session pooler) |
| `DATABASE_URL_SYNC` | `postgresql://postgres.XXXXX:PASS@aws-1-REGION.pooler.supabase.com:5432/postgres` | Same as above, without `+asyncpg` |
| `SUPABASE_URL` | `https://XXXXX.supabase.co` | Supabase → Settings → API → Project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJ...` | Supabase → Settings → API → service_role key |
| `SUPABASE_ANON_KEY` | `eyJ...` | Supabase → Settings → API → anon key |
| `SUPABASE_JWT_SECRET` | `your-jwt-secret` | Supabase → Settings → API → JWT Secret |

> **Note:** `REDIS_URL` is auto-populated from the Redis service. `BASE_URL`, `FRONTEND_URL`, `ENVIRONMENT`, rate limits, and `CORS_ORIGINS` are set in `render.yaml`.

### Step 5.3: Configure Custom Domain

1. Go to **Render Dashboard** → your web service → **Settings** → **Custom Domains**
2. Click **"Add Custom Domain"**
3. Enter `2goi.in`
4. Render will show you the required DNS records (already added in Step 4.2)
5. Wait for SSL certificate to be provisioned (usually 5-10 minutes)
6. Also add `www.2goi.in` as a custom domain

### Step 5.4: Deploy

- **Automatic:** Every `git push` to the connected branch triggers a new build
- **Manual:** Go to the web service → click **"Manual Deploy"** → **"Deploy latest commit"**

Build takes ~3-5 minutes. Monitor the **Logs** tab for any errors.

### Step 5.5: Verify Deployment

After deployment, check:

| URL | Expected Result |
|-----|-----------------|
| `https://2goi.in` | Homepage loads |
| `https://2goi.in/api/health` | `{"status":"healthy","database":"connected","redis":"connected"}` |
| `https://2goi.in/api/docs` | Swagger UI loads |

> **Free tier note:** Render's free tier sleeps after 15 minutes of inactivity. The first request after sleeping takes 30-60 seconds to wake up.

---

## 6. Resend (Email Service)

Resend sends transactional emails (signup confirmation, password reset) from your custom domain.

**Free tier:** 3,000 emails/month — more than enough for most projects.

### Step 6.1: Create Resend Account

1. Go to **https://resend.com/signup**
2. Create a free account (no credit card needed)

### Step 6.2: Add and Verify Your Domain

1. Go to **[resend.com/domains](https://resend.com/domains)**
2. Click **"+ Add domain"**
3. Enter `2goi.in`
4. Resend shows 3 DNS records to add:

| Record | Type | Name | Value |
|--------|------|------|-------|
| DKIM | TXT | `resend._domainkey` | `p=MIGfMA0GCSqG...` (long key) |
| MX | MX | `send` | `feedback-smtp.[region].amazonses.com` (Priority: 10) |
| SPF | TXT | `send` | `v=spf1 include:amazonses.com ~all` |

5. **Quick method:** If GoDaddy offers an "Auto configure" option, click it — it adds all 3 records automatically
6. **Manual method:** Add each record in GoDaddy DNS (see Section 4.2)
7. Wait a few minutes, then click **"Verify"** in Resend
8. All 3 records should turn **green** (Verified)

### Step 6.3: Create an API Key

1. Go to **[resend.com/api-keys](https://resend.com/api-keys)**
2. Click **"Create API Key"**
3. Fill in:
   - **Name:** `supabase`
   - **Permission:** Full access
   - **Domain:** `2goi.in`
4. Click **"Create"**
5. **Copy the API key immediately** (starts with `re_`) — it's only shown once

### Step 6.4: Connect Resend to Supabase

1. Go to **Supabase Dashboard** → **Project Settings** → **Authentication**
2. Scroll down to **SMTP Settings**
3. Toggle **"Enable custom SMTP"** → ON
4. Fill in:

| Field | Value |
|-------|-------|
| **Sender email** | `noreply@2goi.in` |
| **Sender name** | `2GOI` |
| **Host** | `smtp.resend.com` |
| **Port** | `465` |
| **Username** | `resend` |
| **Password** | Your Resend API key (starts with `re_`) |

5. Click **"Save changes"**

### Step 6.5: Enable Email Confirmation

1. Go to **Authentication** → **Providers** → **Email**
2. Turn ON **"Confirm email"**
3. Save

### Step 6.6: Test

1. Go to `https://2goi.in/signup`
2. Sign up with a real email address
3. Check your inbox (may take 1-5 minutes on free tier)
4. You should receive a confirmation email from `noreply@2goi.in`
5. Click the confirmation link
6. Sign in at `https://2goi.in/login`

---

## 7. Google Search Console (SEO)

This makes your site discoverable on Google Search.

### Step 7.1: Add Your Property

1. Go to **https://search.google.com/search-console**
2. Click **"Add Property"**
3. Choose **"URL prefix"** → enter `https://2goi.in`
4. Click **"Continue"**

### Step 7.2: Verify Ownership

**Option A: DNS verification (recommended)**
1. Google gives you a TXT record like `google-site-verification=XXXXX`
2. Add it in GoDaddy DNS:
   - Type: TXT
   - Name: `@`
   - Value: The full verification string
3. Wait a few minutes → click **"Verify"** in Search Console

**Option B: HTML file verification**
1. Google gives you a file like `googleXXXXXXXX.html`
2. Create the file in `frontend/public/` with the content Google specifies
3. Add a route in `backend/app/main.py` to serve it (like we did for `google9b58524465f218d0.html`)
4. Push to GitHub → wait for Render deploy → click **"Verify"**

### Step 7.3: Submit Sitemap

1. In Search Console, go to **Sitemaps** (left sidebar)
2. Enter `sitemap.xml` in the input field
3. Click **"Submit"**
4. Status should show "Success" after Google processes it

### Step 7.4: Request Indexing

1. Go to **URL Inspection** (left sidebar)
2. Enter `https://2goi.in` in the search bar
3. Click **"Request Indexing"**
4. Wait for Google to process (usually 2-7 days)

### SEO Files Already Included

The project already contains these SEO files:

| File | Purpose |
|------|---------|
| `frontend/index.html` | SEO meta tags, Open Graph, Twitter cards, JSON-LD structured data |
| `frontend/public/sitemap.xml` | Lists all public pages for Google crawler |
| `frontend/public/robots.txt` | Allows crawlers, blocks `/api/` endpoints |
| `backend/app/main.py` | Routes for `/robots.txt`, `/sitemap.xml`, and Google verification file |

---

## 8. UptimeRobot (Uptime Monitoring)

UptimeRobot keeps the application alive 24/7 by preventing Render's free tier cold starts.

### Why UptimeRobot Is Needed

Render's free tier has a critical limitation: **it puts your service to sleep after 15 minutes of inactivity**. When the next user visits, they experience a 30-60 second cold start while the Docker container boots up, Python loads, and database connections are established. This creates a terrible user experience.

UptimeRobot solves this by sending a real HTTP request to your health endpoint every 5 minutes. Since Render only checks "has any request arrived in the last 15 minutes?", these pings keep the container running permanently.

### What UptimeRobot Does vs. What Render Does

| Tool | Role | What It Does |
|------|------|--------------|
| **Render** | Hosting | Runs the Docker container, serves the app, provides the URL |
| **UptimeRobot** | Monitoring | Sends HTTP pings every 5 min to prevent Render from sleeping the container |

### Render Challenges Fixed by UptimeRobot

| Render Free Tier Problem | How UptimeRobot Fixes It |
|--------------------------|-------------------------|
| Service sleeps after 15 min inactivity | Pings every 5 min — service never goes idle |
| First request after sleep takes 30-60 sec (cold start) | No cold starts — container stays warm 24/7 |
| Health checks fail during sleep (shows "degraded") | Continuous pings keep health checks green |
| Users think the site is broken/slow | Site always responds instantly (~200-500ms) |

### Step 8.1: Create UptimeRobot Account

1. Go to **https://uptimerobot.com**
2. Click **"Register for FREE"**
3. Sign up with email or Google account
4. Verify your email address

### Step 8.2: Add a Monitor

1. After login, click the green **"+ New"** button (top right)
2. Select **"HTTP(s)"** as the monitor type
3. Fill in the settings:
   - **Friendly Name:** `2goi.in/api/health`
   - **URL to Monitor:** `https://2goi.in/api/health`
   - **Monitoring Interval:** `5 minutes` (free tier minimum)
4. Under **"How will we notify you?"**, check your email
5. Click **"Create Monitor"** or **"Save changes"**

### Step 8.3: Verify It's Working

1. Wait 5-10 minutes for the first few checks to complete
2. Go to **Monitoring** tab in UptimeRobot dashboard
3. Your monitor should show a green **"Up"** status
4. Response time should be ~200-500ms

### Step 8.4: What the Health Endpoint Returns

UptimeRobot pings `GET https://2goi.in/api/health`, which returns:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

If the database or Redis is down, it returns `"degraded"` instead of `"healthy"`. UptimeRobot treats any HTTP 200 response as "Up".

### Important Notes

- **Cost:** Completely free (UptimeRobot free tier supports up to 50 monitors)
- **No code changes needed:** The health endpoint already exists at `/api/health`
- **HEAD + GET support:** The health endpoint accepts both `GET` and `HEAD` HTTP methods for compatibility with all monitoring tools
- **Bonus features:** UptimeRobot provides uptime percentage tracking, response time graphs, and email alerts when the site goes down

---

## 9. Environment Variables Reference

### Backend Variables (set in Render dashboard or `.env` locally)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | Async PostgreSQL connection (asyncpg driver) | `postgresql+asyncpg://user:pass@host:5432/postgres` |
| `DATABASE_URL_SYNC` | Yes | Sync PostgreSQL connection (psycopg2 driver) | `postgresql://user:pass@host:5432/postgres` |
| `SUPABASE_URL` | Yes | Supabase project URL | `https://xxxxx.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Admin key (backend only, NEVER expose) | `eyJ...` |
| `SUPABASE_ANON_KEY` | Yes | Public key (also used in Dockerfile for frontend) | `eyJ...` |
| `SUPABASE_JWT_SECRET` | Yes | JWT secret for HS256 fallback verification | `your-jwt-secret` |
| `REDIS_URL` | Yes | Redis connection string | `redis://red-xxxxx:6379` |
| `BASE_URL` | Yes | Domain for constructing short URLs | `https://2goi.in` |
| `FRONTEND_URL` | Yes | Same as BASE_URL (single-domain) | `https://2goi.in` |
| `ENVIRONMENT` | No | `production` or `development` | `production` |
| `RATE_LIMIT_ANON` | No | Max requests/min for anonymous users | `100` |
| `RATE_LIMIT_AUTH` | No | Max requests/min for authenticated users | `1000` |
| `CORS_ORIGINS` | No | Comma-separated allowed origins | `https://2goi.in` |

### Frontend Variables (set in Dockerfile ENV or `.env` locally)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VITE_API_URL` | No | Backend API URL (empty = same domain) | `` (empty string) |
| `VITE_SUPABASE_URL` | Yes | Supabase project URL (public) | `https://xxxxx.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Yes | Supabase anon key (public) | `eyJ...` |

> **Important:** Frontend variables are embedded at **build time** by Vite. In production, they're set in the `Dockerfile` ENV lines. Changing them requires a rebuild.

---

## 10. Verification Checklist

After completing all setup steps, verify everything works:

### Infrastructure

- [ ] `https://2goi.in` loads the homepage
- [ ] `https://2goi.in/api/health` returns `{"status":"healthy","database":"connected","redis":"connected"}`
- [ ] `https://2goi.in/api/docs` shows Swagger UI
- [ ] `https://2goi.in/robots.txt` returns robots file
- [ ] `https://2goi.in/sitemap.xml` returns sitemap

### Authentication

- [ ] Email/password signup works at `/signup`
- [ ] Confirmation email arrives from `noreply@2goi.in`
- [ ] Email/password login works at `/login`
- [ ] Google OAuth login works (redirects to Google, then back to `/dashboard`)
- [ ] Sign out works
- [ ] Protected routes (`/dashboard`, `/analytics`) redirect to `/login` when not authenticated

### Core Features

- [ ] Shorten a URL on the homepage → get short URL + QR code
- [ ] Click the short URL → redirects to original URL
- [ ] Dashboard shows created links
- [ ] Analytics page shows click data (charts)
- [ ] Delete a link from the dashboard
- [ ] Custom alias works (e.g., `2goi.in/myresume`)
- [ ] Link expiration works (set expires_in, link returns 410 after expiry)

### SEO

- [ ] Google Search Console shows property as verified
- [ ] Sitemap submitted successfully
- [ ] URL inspection shows "URL is on Google" (after a few days)

### Uptime Monitoring

- [ ] UptimeRobot account created
- [ ] Monitor added for `https://2goi.in/api/health`
- [ ] Monitor shows green "Up" status
- [ ] Email notifications enabled

---

## Troubleshooting

### "Error sending confirmation email"
- Verify Resend domain is verified (green status at resend.com/domains)
- Check Supabase SMTP password is the Resend API key (starts with `re_`)
- Username must be literally `resend`, not your email

### "Invalid credentials" on login
- User may not have confirmed their email yet
- Check if "Confirm email" is enabled in Supabase Auth settings
- If enabled, user must click the confirmation link in their email first

### Render deploy fails
- Check the build logs in Render dashboard
- Ensure all environment variables are set (especially DATABASE_URL)
- Verify the Dockerfile builds correctly locally: `docker build -t 2goi .`

### Google OAuth not working
- Ensure the Supabase callback URL is in Google Cloud Console's "Authorized redirect URIs"
- Ensure `2goi.in` and your Supabase URL are in "Authorized JavaScript origins"
- Check that the OAuth consent screen is published (not in "Testing" mode)
- Verify Client ID and Client Secret are correctly pasted in Supabase Auth → Google provider

### Site blocked by corporate firewall (Zscaler, etc.)
- This is your company's web filter, not a site issue
- Use a personal device or mobile hotspot
- Submit a site review request through the block page

### Redis connection issues
- Render free Redis has 25MB limit and no persistence
- If Redis is down, the app falls back to database queries (slower but works)
- Check Render dashboard for Redis service status

### DNS not propagating
- DNS changes can take up to 48 hours (usually 15 min to a few hours)
- Use https://dnschecker.org to check propagation status
- Clear your browser cache and try again

---

## Cost Summary

| Service | Plan | Cost | Limit |
|---------|------|------|-------|
| Supabase | Free | $0/month | 500MB DB, 50,000 auth users |
| Render Web | Free | $0/month | 750 hours/month, sleeps after 15min |
| Render Redis | Free | $0/month | 25MB, no persistence |
| Resend | Free | $0/month | 3,000 emails/month |
| Google Cloud | Free | $0/month | OAuth is free, no limits |
| Google Search Console | Free | $0/forever | Unlimited |
| UptimeRobot | Free | $0/month | 50 monitors, 5-min interval |
| GoDaddy Domain | Paid | ~$8/year | Yearly renewal |
| **Total** | | **~$0.67/month** | |

---

*Built by Badri Pamisetty — https://github.com/Badri-2915/2goi*
