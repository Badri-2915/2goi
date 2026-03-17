"""
Analytics Router — GET /api/analytics/{short_code} endpoint.

Returns detailed click analytics for a specific short link:
- Total clicks
- Country breakdown (top 10)
- Device type breakdown (mobile/tablet/desktop)
- Browser breakdown (top 10)
- Daily click trend (from pre-aggregated table)

Requires authentication. Users can only view analytics for their own links.
The "days" query parameter controls the time range (default 30, max 365).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.auth import require_auth
from app.models.user import User
from app.schemas.click import AnalyticsResponse
from app.services.analytics import get_analytics

router = APIRouter(prefix="/api", tags=["Analytics"])


@router.get("/analytics/{short_code}", response_model=AnalyticsResponse)
async def get_link_analytics(
    short_code: str,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """Get analytics for a short link. Only the link owner can view analytics."""
    analytics = await get_analytics(db, short_code, current_user.id, days)

    if not analytics:
        raise HTTPException(status_code=404, detail="Link not found or access denied")

    return AnalyticsResponse(**analytics)
