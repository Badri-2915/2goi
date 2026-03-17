"""
Redis Client — Async Redis connection for caching short link redirects.

Redis is used as a cache-aside (lazy-loading) cache:
- On redirect: check Redis first (cache hit = sub-5ms response)
- On cache miss: query DB, store result in Redis for next time
- On link creation: prime the cache immediately (write-through)
- On link deletion: invalidate the cache entry

Cache key format: "url:{short_code}" -> original_url
Example: "url:2Bi" -> "https://www.google.com"

Redis failures are always caught and ignored — the app falls back to DB.
This means Redis is optional; the app works without it (just slower).
"""

import redis.asyncio as redis
from app.config import get_settings

settings = get_settings()

# Create async Redis client with automatic reconnection
redis_client = redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",           # Store strings, not bytes
    decode_responses=True,       # Return strings instead of bytes
    socket_connect_timeout=5,    # Don't hang if Redis is down
    retry_on_timeout=True,       # Auto-retry on timeout
)


async def get_redis() -> redis.Redis:
    """FastAPI dependency: returns the shared Redis client instance."""
    return redis_client


async def close_redis():
    """Gracefully close the Redis connection on app shutdown."""
    await redis_client.close()
