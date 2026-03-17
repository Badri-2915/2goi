"""
Analytics Service — Click logging and analytics data retrieval.

This service handles two main responsibilities:

1. LOG CLICKS (log_click function):
   - Parses User-Agent string to extract browser and device type
   - Hashes the IP address (SHA-256) for privacy
   - Inserts a raw click event into the clicks table
   - Upserts the daily_click_stats table (INSERT ON CONFLICT UPDATE)
   - Both operations happen in a single DB transaction

2. GET ANALYTICS (get_analytics function):
   - Returns total clicks, country breakdown, device breakdown, browser breakdown
   - Daily click trend uses the pre-aggregated daily_click_stats table
     (O(days) query instead of scanning O(total_clicks) raw events)

The daily aggregation pattern:
   INSERT INTO daily_click_stats (link_id, date, click_count) VALUES (?, today, 1)
   ON CONFLICT (link_id, date) DO UPDATE SET click_count = click_count + 1
"""

from datetime import datetime, date
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, cast, Date, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert
from user_agents import parse as parse_user_agent

from app.models.click import Click
from app.models.link import Link
from app.models.daily_stats import DailyClickStats
from app.services.shortener import hash_ip


async def log_click(
    db: AsyncSession,
    link_id: UUID,
    ip_address: Optional[str] = None,
    user_agent_string: Optional[str] = None,
    referrer: Optional[str] = None,
    country: Optional[str] = None,
):
    """
    Log a single click event. Called asynchronously via BackgroundTasks
    so it doesn't slow down the redirect response.

    This function does two things in one transaction:
    1. Inserts a raw click row (for detailed per-click analytics)
    2. Upserts daily_click_stats (for fast daily trend queries)
    """
    # Parse User-Agent to get browser name and device type
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

    # Hash the IP for privacy (we never store raw IP addresses)
    ip_hashed = hash_ip(ip_address) if ip_address else None

    # Insert raw click event into the clicks table
    click = Click(
        link_id=link_id,
        country=country or "Unknown",
        browser=browser or "Unknown",
        device_type=device_type or "Unknown",
        referrer=referrer,
        ip_hash=ip_hashed,
    )

    db.add(click)

    # Upsert daily click aggregation using PostgreSQL INSERT ... ON CONFLICT
    # If row exists for (link_id, today): increment click_count
    # If row doesn't exist: create new row with click_count=1
    today = date.today()
    stmt = pg_insert(DailyClickStats).values(
        link_id=link_id, date=today, click_count=1
    )
    stmt = stmt.on_conflict_do_update(
        constraint="uq_daily_stats_link_date",
        set_={"click_count": DailyClickStats.click_count + 1},
    )
    await db.execute(stmt)

    await db.commit()


async def get_analytics(
    db: AsyncSession,
    short_code: str,
    user_id: Optional[UUID] = None,
    days: int = 30,
):
    """
    Get complete analytics for a short link.

    Returns:
    - total_clicks: Total number of clicks ever
    - countries: Top 10 countries by click count
    - devices: Breakdown by device type (mobile/tablet/desktop)
    - browsers: Top 10 browsers by click count
    - daily_clicks: Click count per day (from pre-aggregated table, very fast)
    """
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

    # Daily clicks from pre-aggregated table (fast O(days) query)
    daily_result = await db.execute(
        select(DailyClickStats.date, DailyClickStats.click_count)
        .where(DailyClickStats.link_id == link.id)
        .order_by(DailyClickStats.date.desc())
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
