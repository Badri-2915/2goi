import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, Boolean, DateTime, Text, Sequence
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

# PostgreSQL sequence for Base62 ID generation
link_seq = Sequence("link_id_seq", start=10000, increment=1)


class Link(Base):
    __tablename__ = "links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sequence_id = Column(BigInteger, link_seq, server_default=link_seq.next_value(), unique=True, nullable=False)
    original_url = Column(Text, nullable=False)
    short_code = Column(String(20), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    click_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)

    clicks = relationship("Click", back_populates="link", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Link {self.short_code} -> {self.original_url[:50]}>"
