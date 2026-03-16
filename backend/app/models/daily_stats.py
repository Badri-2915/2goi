import uuid
from datetime import date
from sqlalchemy import Column, Integer, Date, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class DailyClickStats(Base):
    __tablename__ = "daily_click_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    link_id = Column(UUID(as_uuid=True), ForeignKey("links.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    click_count = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint("link_id", "date", name="uq_daily_stats_link_date"),
    )

    def __repr__(self):
        return f"<DailyClickStats link={self.link_id} date={self.date} clicks={self.click_count}>"
