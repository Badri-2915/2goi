from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.auth import require_auth
from app.models.user import User
from app.schemas.link import LinkResponse, LinkListResponse
from app.services.shortener import get_user_links, soft_delete_link
from app.redis_client import get_redis
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api", tags=["Links"])


@router.get("/links", response_model=LinkListResponse)
async def list_user_links(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", pattern="^(created_at|click_count|expires_at)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    links, total = await get_user_links(db, current_user.id, page, page_size, sort_by)

    link_responses = [
        LinkResponse(
            id=link.id,
            original_url=link.original_url,
            short_code=link.short_code,
            short_url=f"{settings.BASE_URL}/{link.short_code}",
            click_count=link.click_count,
            is_active=link.is_active,
            created_at=link.created_at,
            expires_at=link.expires_at,
        )
        for link in links
    ]

    return LinkListResponse(
        links=link_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.delete("/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    link_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    from sqlalchemy import select
    from app.models.link import Link

    # Get the link to find its short_code for cache invalidation
    result = await db.execute(
        select(Link).where(Link.id == link_id, Link.user_id == current_user.id)
    )
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    short_code = link.short_code
    deleted = await soft_delete_link(db, link_id, current_user.id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Link not found")

    # Remove from Redis cache
    redis = await get_redis()
    try:
        await redis.delete(f"url:{short_code}")
    except Exception:
        pass

    return None
