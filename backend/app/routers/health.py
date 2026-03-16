from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db
from app.redis_client import get_redis

router = APIRouter(tags=["Health"])


@router.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    status = {"status": "healthy", "database": "unknown", "redis": "unknown"}

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        status["database"] = "connected"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
        status["status"] = "degraded"

    # Check Redis
    try:
        redis = await get_redis()
        await redis.ping()
        status["redis"] = "connected"
    except Exception as e:
        status["redis"] = f"error: {str(e)}"
        status["status"] = "degraded"

    return status
