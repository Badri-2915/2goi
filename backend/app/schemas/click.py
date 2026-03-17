"""
Click Schemas — Pydantic models for click and analytics data.

These schemas define the response shapes for analytics endpoints:
- ClickResponse: Single click event (not currently used in API, but available)
- CountryBreakdown: Country name + click count
- DeviceBreakdown: Device type + click count
- BrowserBreakdown: Browser name + click count
- DailyClicks: Date + click count (from pre-aggregated table)
- AnalyticsResponse: Complete analytics for GET /api/analytics/{short_code}
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class ClickResponse(BaseModel):
    """Single click event details."""
    id: UUID
    link_id: UUID
    country: Optional[str] = None
    browser: Optional[str] = None
    device_type: Optional[str] = None
    referrer: Optional[str] = None
    clicked_at: datetime

    class Config:
        from_attributes = True


class CountryBreakdown(BaseModel):
    """Country name and its click count (e.g., {"country": "US", "count": 42})."""
    country: str
    count: int


class DeviceBreakdown(BaseModel):
    """Device type and its click count (e.g., {"device_type": "mobile", "count": 28})."""
    device_type: str
    count: int


class BrowserBreakdown(BaseModel):
    """Browser name and its click count (e.g., {"browser": "Chrome", "count": 35})."""
    browser: str
    count: int


class DailyClicks(BaseModel):
    """Daily click count (e.g., {"date": "2026-03-17", "count": 15})."""
    date: str
    count: int


class AnalyticsResponse(BaseModel):
    """Complete analytics response for a short link."""
    short_code: str
    total_clicks: int
    countries: list[CountryBreakdown]
    devices: list[DeviceBreakdown]
    browsers: list[BrowserBreakdown]
    daily_clicks: list[DailyClicks]
