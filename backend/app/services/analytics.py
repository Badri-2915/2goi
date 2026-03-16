from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from user_agents import parse as parse_user_agent

from app.models.click import Click
from app.models.link import Link
from app.services.shortener import hash_ip


async def log_click(
    db: AsyncSession,
    link_id: UUID,
    ip_address: Optional[str] = None,
    user_agent_string: Optional[str] = None,
    referrer: Optional[str] = None,
    country: Optional[str] = None,
):
    browser = None
    device_type = None

    if user_agent_string:
        ua = parse_user_agent(user_agent_string)
        browser = ua.browser.family
        if ua.is_mobile:
            device_type = "mobile"
        elif ua.is_tablet:
            device_type = "tablet"
        else:
            device_type = "desktop"

    ip_hashed = hash_ip(ip_address) if ip_address else None

    click = Click(
        link_id=link_id,
        country=country or "Unknown",
        browser=browser or "Unknown",
        device_type=device_type or "Unknown",
        referrer=referrer,
        ip_hash=ip_hashed,
    )

    db.add(click)
    await db.commit()


async def get_analytics(
    db: AsyncSession,
    short_code: str,
    user_id: Optional[UUID] = None,
    days: int = 30,
):
    # Get the link
    query = select(Link).where(Link.short_code == short_code, Link.is_active == True)
    if user_id:
        query = query.where(Link.user_id == user_id)

    result = await db.execute(query)
    link = result.scalar_one_or_none()
    if not link:
        return None

    # Total clicks
    total_result = await db.execute(
        select(func.count(Click.id)).where(Click.link_id == link.id)
    )
    total_clicks = total_result.scalar() or 0

    # Country breakdown
    country_result = await db.execute(
        select(Click.country, func.count(Click.id).label("count"))
        .where(Click.link_id == link.id)
        .group_by(Click.country)
        .order_by(func.count(Click.id).desc())
        .limit(10)
    )
    countries = [{"country": row[0] or "Unknown", "count": row[1]} for row in country_result.all()]

    # Device breakdown
    device_result = await db.execute(
        select(Click.device_type, func.count(Click.id).label("count"))
        .where(Click.link_id == link.id)
        .group_by(Click.device_type)
        .order_by(func.count(Click.id).desc())
    )
    devices = [{"device_type": row[0] or "Unknown", "count": row[1]} for row in device_result.all()]

    # Browser breakdown
    browser_result = await db.execute(
        select(Click.browser, func.count(Click.id).label("count"))
        .where(Click.link_id == link.id)
        .group_by(Click.browser)
        .order_by(func.count(Click.id).desc())
        .limit(10)
    )
    browsers = [{"browser": row[0] or "Unknown", "count": row[1]} for row in browser_result.all()]

    # Daily clicks (last N days)
    daily_result = await db.execute(
        select(
            cast(Click.clicked_at, Date).label("date"),
            func.count(Click.id).label("count"),
        )
        .where(Click.link_id == link.id)
        .group_by(cast(Click.clicked_at, Date))
        .order_by(cast(Click.clicked_at, Date).desc())
        .limit(days)
    )
    daily_clicks = [
        {"date": str(row[0]), "count": row[1]}
        for row in daily_result.all()
    ]
    daily_clicks.reverse()

    return {
        "short_code": short_code,
        "total_clicks": total_clicks,
        "countries": countries,
        "devices": devices,
        "browsers": browsers,
        "daily_clicks": daily_clicks,
    }
