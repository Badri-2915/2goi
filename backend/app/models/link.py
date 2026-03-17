"""
Link Model — The core table for storing shortened URLs.

Each link has:
- A UUID primary key (for safe external exposure in APIs)
- A sequential integer ID (sequence_id) used for Base62 short code generation
- The original long URL and its corresponding short code
- An optional user_id (links can be anonymous or user-owned)
- Click count, active flag, timestamps, and optional expiration

The sequence_id starts at 10000 to guarantee minimum 3-character Base62 codes.
Example: sequence_id 10008 -> Base62 "2Bq"
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, Boolean, DateTime, Text, Sequence
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

# PostgreSQL sequence for Base62 ID generation
# Starts at 10000 so all generated codes are at least 3 characters long
link_seq = Sequence("link_id_seq", start=10000, increment=1)


class Link(Base):
    __tablename__ = "links"

    # UUID primary key — safe to expose in APIs, not guessable
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Auto-incrementing integer used for deterministic Base62 short code generation
    # This eliminates collision checks — each ID maps to exactly one unique short code
    sequence_id = Column(BigInteger, link_seq, server_default=link_seq.next_value(), unique=True, nullable=False)

    # The original long URL that the short link redirects to
    original_url = Column(Text, nullable=False)

    # The short code (e.g., "2Bq" or a custom alias like "myresume")
    short_code = Column(String(20), unique=True, nullable=False, index=True)

    # Owner of the link (nullable — anonymous users can also create links)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Total number of times this short link has been clicked
    click_count = Column(Integer, default=0, nullable=False)

    # Soft delete flag — deactivated links return 404 but data is preserved
    is_active = Column(Boolean, default=True, nullable=False)

    # When the link was created
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Optional expiration — expired links return HTTP 410 Gone
    expires_at = Column(DateTime, nullable=True)

    # One-to-many relationship: a link has many clicks
    clicks = relationship("Click", back_populates="link", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Link {self.short_code} -> {self.original_url[:50]}>"
