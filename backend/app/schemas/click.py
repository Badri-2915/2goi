from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class ClickResponse(BaseModel):
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
    country: str
    count: int


class DeviceBreakdown(BaseModel):
    device_type: str
    count: int


class BrowserBreakdown(BaseModel):
    browser: str
    count: int


class DailyClicks(BaseModel):
    date: str
    count: int


class AnalyticsResponse(BaseModel):
    short_code: str
    total_clicks: int
    countries: list[CountryBreakdown]
    devices: list[DeviceBreakdown]
    browsers: list[BrowserBreakdown]
    daily_clicks: list[DailyClicks]
