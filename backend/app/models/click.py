import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Click(Base):
    __tablename__ = "clicks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    link_id = Column(UUID(as_uuid=True), ForeignKey("links.id", ondelete="CASCADE"), nullable=False, index=True)
    country = Column(String(10), nullable=True)
    browser = Column(String(50), nullable=True)
    device_type = Column(String(20), nullable=True)
    referrer = Column(String(2048), nullable=True)
    ip_hash = Column(String(64), nullable=True)
    clicked_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    link = relationship("Link", back_populates="clicks")

    def __repr__(self):
        return f"<Click {self.id} on {self.link_id}>"
