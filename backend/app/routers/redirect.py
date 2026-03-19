"""
Redirect Router — GET /{short_code} endpoint (the core of the URL shortener).

This is the most performance-critical endpoint. When someone visits
https://2goi.in/2Bi, this router:

1. Checks Redis cache first (cache hit = sub-5ms response)
2. On cache miss, queries the database
3. Stores the result in Redis for next time
4. Logs the click asynchronously (doesn't slow down the redirect)
5. Returns HTTP 302 redirect to the original URL

Important: This router uses a catch-all pattern (/{short_code}), so it MUST
be registered LAST in main.py to avoid intercepting API and frontend routes.
It explicitly skips paths like "api", "login", "dashboard", "assets", etc.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, AsyncSessionLocal
from app.services.shortener import get_link_by_code, increment_click_count
from app.services.analytics import log_click
from app.redis_client import get_redis
from app.auth import get_client_ip

router = APIRouter(tags=["Redirect"])


async def _log_click_background(
    link_id,
    ip_address: str,
    user_agent: str,
    referrer: str,
):
    """
    Background task: log click analytics after the redirect response is sent.
    Uses its own DB session since BackgroundTasks run after the response.
    """
    async with AsyncSessionLocal() as db:
        await log_click(
            db=db,
            link_id=link_id,
            ip_address=ip_address,
            user_agent_string=user_agent,
            referrer=referrer,
        )
        await increment_click_count(db, link_id)


@router.get("/{short_code}")
async def redirect_short_url(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Redirect a short URL to its original destination. Returns HTTP 302."""
    # Skip API paths and frontend routes (these should NOT be treated as short codes)
    frontend_routes = {"login", "signup", "dashboard", "analytics", "favicon.svg", "assets", "sitemap.xml", "robots.txt", "google9b58524465f218d0.html"}
    if short_code.startswith("api") or short_code in frontend_routes or short_code.startswith("assets") or "." in short_code:
        raise HTTPException(status_code=404, detail="Not found")

    # Step 1: Check Redis cache
    redis = await get_redis()
    try:
        cached_url = await redis.get(f"url:{short_code}")
    except Exception:
        cached_url = None

    if cached_url:
        # Cache hit — get link_id from DB for analytics (async)
        link = await get_link_by_code(db, short_code)
        if link:
            background_tasks.add_task(
                _log_click_background,
                link.id,
                get_client_ip(request),
                request.headers.get("user-agent", ""),
                request.headers.get("referer", ""),
            )
        return RedirectResponse(url=cached_url, status_code=302)

    # Step 2: Cache miss — query database
    link = await get_link_by_code(db, short_code)

    if not link:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Check expiration
    if link.expires_at and link.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="This link has expired")

    # Store in Redis for next time
    try:
        if link.expires_at:
            ttl = int((link.expires_at - datetime.utcnow()).total_seconds())
            if ttl > 0:
                await redis.setex(f"url:{short_code}", ttl, link.original_url)
        else:
            await redis.set(f"url:{short_code}", link.original_url)
    except Exception:
        pass  # Redis failure should not break redirect

    # Log click asynchronously
    background_tasks.add_task(
        _log_click_background,
        link.id,
        get_client_ip(request),
        request.headers.get("user-agent", ""),
        request.headers.get("referer", ""),
    )

    return RedirectResponse(url=link.original_url, status_code=302)
