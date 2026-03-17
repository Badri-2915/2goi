"""
User Model — Stores user accounts synced from Supabase Auth.

When a user signs up via Supabase (email/password or Google OAuth),
their account is automatically created here on first API request.
The UUID matches the Supabase auth.users.id so both systems stay in sync.

Users can have a plan ("free" by default) for future rate limit tiers.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class User(Base):
    __tablename__ = "users"

    # UUID from Supabase Auth — same as auth.users.id for consistency
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User's email address (unique, indexed for fast lookups)
    email = Column(String(255), unique=True, nullable=False, index=True)

    # Subscription plan: "free" by default, can be extended for premium tiers
    plan = Column(String(20), default="free", nullable=False)

    # When the user first signed up
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"
