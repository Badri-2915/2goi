"""
Link Schemas — Pydantic models for request/response validation.

These schemas define the shape of JSON data flowing through the API:
- LinkCreate: Input for POST /api/shorten (URL, optional alias, optional TTL)
- ShortenResponse: Output of POST /api/shorten (short_url, QR code, etc.)
- LinkResponse: Single link in GET /api/links response
- LinkListResponse: Paginated list of links

Pydantic automatically validates all incoming data and returns
clear error messages if validation fails (e.g., invalid URL format).
"""

from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
import re


class LinkCreate(BaseModel):
    """Request body for POST /api/shorten."""
    url: str = Field(..., description="The original URL to shorten")
    custom_alias: Optional[str] = Field(None, max_length=20, description="Optional custom short code")
    expires_in: Optional[int] = Field(None, gt=0, description="Expiration time in seconds")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        """Ensure URL starts with http:// or https:// and has a valid domain."""
        pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        if not pattern.match(v):
            raise ValueError("Invalid URL format. Must start with http:// or https://")
        return v

    @field_validator("custom_alias")
    @classmethod
    def validate_alias(cls, v):
        """Custom alias must be 3+ chars, alphanumeric + hyphens only."""
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9\-]+$', v):
                raise ValueError("Custom alias can only contain letters, numbers, and hyphens")
            if len(v) < 3:
                raise ValueError("Custom alias must be at least 3 characters")
        return v


class LinkResponse(BaseModel):
    """Single link object returned in API responses."""
    id: UUID
    original_url: str
    short_code: str
    short_url: str
    click_count: int
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LinkListResponse(BaseModel):
    """Paginated list of links returned by GET /api/links."""
    links: list[LinkResponse]
    total: int
    page: int
    page_size: int


class ShortenResponse(BaseModel):
    """Response from POST /api/shorten with the new short link and QR code."""
    short_url: str
    short_code: str
    original_url: str
    qr_code: str
    expires_at: Optional[datetime] = None
