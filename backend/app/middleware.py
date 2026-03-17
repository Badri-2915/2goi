"""
Middleware Module — Rate limiting configuration.

Uses SlowAPI (built on top of limits library) to enforce rate limits:
- Anonymous users: 100 requests/minute (configurable via RATE_LIMIT_ANON)
- Authenticated users: 1000 requests/minute (configurable via RATE_LIMIT_AUTH)

Rate limits are tracked per IP address. Behind reverse proxies (like Render),
we extract the real IP from the X-Forwarded-For header.

When rate limit is exceeded, returns HTTP 429 (Too Many Requests).
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse


def get_real_ip(request: Request) -> str:
    """Extract real client IP from X-Forwarded-For header (for reverse proxy support)."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# Rate limiter instance — uses real IP as the rate limit key
limiter = Limiter(key_func=get_real_ip)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for HTTP 429 Too Many Requests."""
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )
