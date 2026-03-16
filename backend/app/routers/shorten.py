from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.schemas.link import LinkCreate, ShortenResponse
from app.services.shortener import create_short_link, generate_qr_code
from app.redis_client import get_redis
from app.config import get_settings

settings = get_settings()
router = APIRouter(tags=["Shorten"])


@router.post("/api/shorten", response_model=ShortenResponse, status_code=status.HTTP_201_CREATED)
async def shorten_url(
    payload: LinkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    try:
        user_id = current_user.id if current_user else None
        link = await create_short_link(
            db=db,
            original_url=payload.url,
            custom_alias=payload.custom_alias,
            expires_in=payload.expires_in,
            user_id=user_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    short_url = f"{settings.BASE_URL}/{link.short_code}"

    # Prime Redis cache
    redis = await get_redis()
    try:
        if link.expires_at:
            ttl = int((link.expires_at - link.created_at).total_seconds())
            await redis.setex(f"url:{link.short_code}", ttl, link.original_url)
        else:
            await redis.set(f"url:{link.short_code}", link.original_url)
    except Exception:
        pass  # Redis failure should not break link creation

    # Generate QR code
    qr_code = generate_qr_code(short_url)

    return ShortenResponse(
        short_url=short_url,
        short_code=link.short_code,
        original_url=link.original_url,
        qr_code=qr_code,
        expires_at=link.expires_at,
    )
