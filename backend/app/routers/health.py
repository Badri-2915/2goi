"""
Health Router — GET /api/health endpoint.

Returns the health status of the application, including:
- Database connectivity (runs SELECT 1)
- Redis connectivity (runs PING)

Used by Render's health check to know if the service is running.
If any dependency is down, status becomes "degraded" instead of "healthy".

Sample response:
  {"status": "healthy", "database": "connected", "redis": "connected"}
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db
from app.redis_client import get_redis

router = APIRouter(tags=["Health"])


@router.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Check database and Redis connectivity. Used by Render health checks."""
    status = {"status": "healthy", "database": "unknown", "redis": "unknown"}

    # Check database connectivity
    try:
        await db.execute(text("SELECT 1"))
        status["database"] = "connected"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
        status["status"] = "degraded"

    # Check Redis connectivity
    try:
        redis = await get_redis()
        await redis.ping()
        status["redis"] = "connected"
    except Exception as e:
        status["redis"] = f"error: {str(e)}"
        status["status"] = "degraded"

    return status
