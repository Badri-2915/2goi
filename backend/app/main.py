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

# Path to the React frontend build directory
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables (gracefully handle DB unavailability)
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
    # Shutdown: close connections
    try:
        await close_redis()
    except Exception:
        pass
    try:
        await engine.dispose()
    except Exception:
        pass


app = FastAPI(
    title="2GOI URL Shortener API",
    description="Production-grade URL shortening platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
origins = settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers — order matters! API routes first, then catch-all redirect
app.include_router(health.router)
app.include_router(shorten.router)
app.include_router(links.router)
app.include_router(analytics.router)
app.include_router(redirect.router)

# Serve frontend static assets (JS, CSS, images)
if STATIC_DIR.exists() and (STATIC_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="static-assets")


@app.get("/favicon.svg")
async def favicon():
    favicon_path = STATIC_DIR / "favicon.svg"
    if favicon_path.exists():
        return FileResponse(str(favicon_path))
    return {"detail": "Not found"}


@app.get("/")
async def root():
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
    """Serve React SPA for any unmatched routes (frontend routing)."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists() and not request.url.path.startswith("/api"):
        return FileResponse(str(index_path))
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=404, content={"detail": "Not found"})
