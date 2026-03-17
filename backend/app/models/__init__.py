"""
Models Package — All SQLAlchemy models are registered here.

Importing models here ensures SQLAlchemy discovers them during
Base.metadata.create_all() at application startup, so tables
are automatically created if they don't exist.
"""

from app.models.link import Link
from app.models.click import Click
from app.models.user import User
from app.models.daily_stats import DailyClickStats

__all__ = ["Link", "Click", "User", "DailyClickStats"]
