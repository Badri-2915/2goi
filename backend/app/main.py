"""
Main Application — FastAPI app setup and single-domain architecture.

This is the entry point for the entire application. It configures:
1. FastAPI app with lifespan (startup/shutdown events)
2. CORS middleware for cross-origin requests
3. Rate limiting via SlowAPI
4. API routers (shorten, redirect, links, analytics, health)
5. Static file serving for the React frontend (SPA)
6. SPA fallback: any unmatched route serves index.html (for React Router)

Single-Domain Architecture:
  Everything runs on one domain (2goi.in):
  - /api/*        → Backend API endpoints
  - /assets/*     → Frontend static files (JS, CSS, images)
  - /login, /dashboard, etc. → React SPA (served via index.html)
  - /{short_code} → Redirect to original URL
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.database import engine, Base
from app.redis_client import close_redis
from app.middleware import limiter
from app.routers import shorten, redirect, links, analytics, health

settings = get_settings()

# Path to the React frontend build directory (copied during Docker build)
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: runs on startup and shutdown."""
    # STARTUP: Create database tables if they don't exist
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables created/verified successfully")
    except Exception as e:
        print(f"Warning: Could not connect to database on startup: {e}")
        print("Tables must be created manually via supabase/migrations/001_initial_schema.sql")

    # Check if frontend static files exist
    if STATIC_DIR.exists():
        print(f"Serving frontend from {STATIC_DIR}")
    else:
        print(f"Warning: Frontend static dir not found at {STATIC_DIR}")

    yield
    # SHUTDOWN: Gracefully close all connections
    try:
        await close_redis()
    except Exception:
        pass
    try:
        await engine.dispose()
    except Exception:
        pass


# Create the FastAPI application
# API docs are served at /api/docs (Swagger) and /api/redoc (ReDoc)
app = FastAPI(
    title="2GOI URL Shortener API",
    description="Production-grade URL shortening platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Rate limiter — prevents abuse (100 req/min anonymous, 1000 req/min authenticated)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — allow requests from configured origins (same domain in production)
origins = settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers — ORDER MATTERS!
# API routes must be registered before the catch-all redirect router,
# otherwise /{short_code} would intercept API paths
app.include_router(health.router)      # GET /api/health
app.include_router(shorten.router)     # POST /api/shorten
app.include_router(links.router)       # GET /api/links, DELETE /api/links/{id}
app.include_router(analytics.router)   # GET /api/analytics/{short_code}
app.include_router(redirect.router)    # GET /{short_code} (catch-all, must be last)

# Serve frontend static assets (Vite build output: JS bundles, CSS, images)
if STATIC_DIR.exists() and (STATIC_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="static-assets")


@app.get("/favicon.svg")
async def favicon():
    favicon_path = STATIC_DIR / "favicon.svg"
    if favicon_path.exists():
        return FileResponse(str(favicon_path))
    return {"detail": "Not found"}


@app.get("/robots.txt")
async def robots():
    """Serve robots.txt for search engine crawlers."""
    robots_path = STATIC_DIR / "robots.txt"
    if robots_path.exists():
        return FileResponse(str(robots_path), media_type="text/plain")
    return {"detail": "Not found"}


@app.get("/sitemap.xml")
async def sitemap():
    """Serve sitemap.xml for search engine indexing."""
    sitemap_path = STATIC_DIR / "sitemap.xml"
    if sitemap_path.exists():
        return FileResponse(str(sitemap_path), media_type="application/xml")
    return {"detail": "Not found"}


@app.get("/")
async def root():
    """Serve the React SPA homepage (or API info if no frontend build exists)."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {
        "name": "2GOI URL Shortener",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health",
    }


@app.exception_handler(404)
async def spa_fallback(request: Request, exc):
    """
    SPA Fallback: Serve index.html for any unmatched non-API routes.
    This allows React Router to handle client-side routing.
    Example: /login, /dashboard, /analytics/abc → all serve index.html
    """
    index_path = STATIC_DIR / "index.html"
    if index_path.exists() and not request.url.path.startswith("/api"):
        return FileResponse(str(index_path))
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=404, content={"detail": "Not found"})
