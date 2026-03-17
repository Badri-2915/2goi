"""
Click Model — Stores every individual click event on a short link.

Each click records:
- Which link was clicked (link_id)
- Geographic info (country)
- Browser and device type (parsed from User-Agent header)
- Referrer URL (where the click came from)
- Hashed IP address (SHA-256 for privacy, no raw IPs stored)
- Timestamp of the click

This is the raw data table. For fast analytics queries, we also maintain
a pre-aggregated daily_click_stats table (see daily_stats.py).
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Click(Base):
    __tablename__ = "clicks"

    # Unique ID for each click event
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Which short link was clicked (foreign key to links table)
    link_id = Column(UUID(as_uuid=True), ForeignKey("links.id", ondelete="CASCADE"), nullable=False, index=True)

    # Country of the visitor (e.g., "US", "IN", "Unknown")
    country = Column(String(10), nullable=True)

    # Browser name parsed from User-Agent (e.g., "Chrome", "Safari")
    browser = Column(String(50), nullable=True)

    # Device type: "mobile", "tablet", or "desktop"
    device_type = Column(String(20), nullable=True)

    # The URL the user came from (HTTP Referer header)
    referrer = Column(String(2048), nullable=True)

    # SHA-256 hash of visitor IP (privacy-safe, no raw IPs stored)
    ip_hash = Column(String(64), nullable=True)

    # When the click happened (indexed for time-range queries)
    clicked_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Many-to-one relationship back to the Link
    link = relationship("Link", back_populates="clicks")

    def __repr__(self):
        return f"<Click {self.id} on {self.link_id}>"
