import redis.asyncio as redis
from app.config import get_settings

settings = get_settings()

redis_client = redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    socket_connect_timeout=5,
    retry_on_timeout=True,
)


async def get_redis() -> redis.Redis:
    return redis_client


async def close_redis():
    await redis_client.close()
