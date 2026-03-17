"""
DailyClickStats Model — Pre-aggregated daily click counts per link.

Instead of scanning the entire clicks table for analytics (which would be
slow at scale: O(total_clicks)), we maintain this summary table that stores
one row per link per day with the total click count.

On each click, we do an INSERT ... ON CONFLICT UPDATE (upsert):
- If no row exists for (link_id, today), insert with click_count=1
- If a row already exists, increment click_count by 1

This makes analytics queries O(days) instead of O(clicks) — a huge speedup.

Example: If link "abc" gets 10,000 clicks over 30 days, we only have 30 rows
here instead of scanning 10,000 rows in the clicks table.
"""

import uuid
from datetime import date
from sqlalchemy import Column, Integer, Date, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class DailyClickStats(Base):
    __tablename__ = "daily_click_stats"

    # Unique ID for each daily aggregation row
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Which link this daily stat belongs to
    link_id = Column(UUID(as_uuid=True), ForeignKey("links.id", ondelete="CASCADE"), nullable=False, index=True)

    # The calendar date (e.g., 2026-03-17)
    date = Column(Date, nullable=False, index=True)

    # Total clicks on this link for this date
    click_count = Column(Integer, default=0, nullable=False)

    # Unique constraint on (link_id, date) — enables the upsert pattern
    # PostgreSQL uses this constraint for INSERT ... ON CONFLICT DO UPDATE
    __table_args__ = (
        UniqueConstraint("link_id", "date", name="uq_daily_stats_link_date"),
    )

    def __repr__(self):
        return f"<DailyClickStats link={self.link_id} date={self.date} clicks={self.click_count}>"
