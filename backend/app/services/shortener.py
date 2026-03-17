"""
Shortener Service — Core business logic for creating and managing short links.

Key features:
- Base62 encoding: Converts sequential DB IDs into short alphanumeric codes
- QR code generation: Every short link gets a downloadable QR code
- Custom aliases: Users can pick their own short codes (e.g., "myresume")
- Link expiration: Optional TTL support
- Soft delete: Links are deactivated, not permanently removed

How Base62 works:
  1. User submits a URL to shorten
  2. We insert a row into the DB (sequence_id is auto-generated: 10000, 10001, ...)
  3. We convert sequence_id to Base62: 10000 -> "2Bi", 10001 -> "2Bj", etc.
  4. The Base62 string becomes the short code
  5. No collision checks needed — each ID maps to exactly one unique code

Why Base62 over random codes?
  - Zero collisions (deterministic, not random)
  - Zero extra DB queries (no need to check if code already exists)
  - Predictable code length (3-6 chars for millions of links)
  - Same approach used by Bitly, TinyURL, and YouTube
"""

import hashlib
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.link import Link
from app.config import get_settings

settings = get_settings()

# Base62 alphabet: digits + lowercase + uppercase = 62 characters
# This gives us 62^3 = 238K codes with 3 chars, 62^5 = 916M with 5 chars
BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def encode_base62(num: int) -> str:
    """
    Encode an integer to a Base62 string.

    Used with sequential DB IDs to generate collision-free short codes.
    Example: 10000 -> "2Bi", 10001 -> "2Bj", 99999 -> "q0T"

    Args:
        num: A positive integer (typically the sequence_id from the DB)

    Returns:
        A short alphanumeric string (e.g., "2Bi")
    """
    if num == 0:
        return BASE62_ALPHABET[0]
    base = len(BASE62_ALPHABET)  # 62
    encoded = []
    while num:
        num, rem = divmod(num, base)  # Get remainder (maps to one character)
        encoded.append(BASE62_ALPHABET[rem])
    return ''.join(reversed(encoded))  # Reverse because we built it backwards


def generate_qr_code(url: str) -> str:
    """
    Generate a QR code image for the given URL and return as Base64 string.

    The QR code is rendered as a PNG image, then encoded to Base64 so it can
    be sent directly in the JSON API response and displayed in the frontend
    as an <img src="data:image/png;base64,..."> tag.
    """
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def hash_ip(ip: str) -> str:
    """Hash an IP address with SHA-256 for privacy. We never store raw IPs."""
    return hashlib.sha256(ip.encode()).hexdigest()


async def create_short_link(
    db: AsyncSession,
    original_url: str,
    custom_alias: Optional[str] = None,
    expires_in: Optional[int] = None,
    user_id: Optional[UUID] = None,
) -> Link:
    """
    Create a new short link.

    Flow:
    1. If custom alias given, check it's not already taken
    2. Insert the link row with a temporary short_code ("__pending__")
    3. DB auto-generates sequence_id (e.g., 10005)
    4. Encode sequence_id to Base62 (e.g., 10005 -> "2Bl")
    5. Update short_code with the Base62 string
    6. Return the complete link object
    """
    # Step 1: Check if custom alias is already taken
    if custom_alias:
        existing = await db.execute(
            select(Link).where(Link.short_code == custom_alias)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Custom alias '{custom_alias}' is already taken")

    expires_at = None
    if expires_in:
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    # Step 2: Insert with temporary placeholder (gets real code after flush)
    link = Link(
        original_url=original_url,
        short_code=custom_alias or "__pending__",
        user_id=user_id,
        click_count=0,
        is_active=True,
        expires_at=expires_at,
    )

    db.add(link)
    await db.flush()  # Step 3: Flush to trigger PostgreSQL sequence and get sequence_id

    # Step 4: Generate short_code from sequence_id using Base62 encoding
    if not custom_alias:
        link.short_code = encode_base62(link.sequence_id)

    # Step 5: Save to database and return the complete link
    await db.commit()
    await db.refresh(link)
    return link


async def get_link_by_code(db: AsyncSession, short_code: str) -> Optional[Link]:
    """Look up an active link by its short code. Returns None if not found or deactivated."""
    result = await db.execute(
        select(Link).where(
            Link.short_code == short_code,
            Link.is_active == True,
        )
    )
    return result.scalar_one_or_none()


async def get_user_links(
    db: AsyncSession,
    user_id: UUID,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
) -> tuple[list[Link], int]:
    """
    Get paginated list of links owned by a user.
    Returns (list_of_links, total_count) for pagination.
    """
    # Count total
    count_result = await db.execute(
        select(func.count(Link.id)).where(
            Link.user_id == user_id,
            Link.is_active == True,
        )
    )
    total = count_result.scalar()

    # Get paginated results
    sort_column = getattr(Link, sort_by, Link.created_at)
    result = await db.execute(
        select(Link)
        .where(Link.user_id == user_id, Link.is_active == True)
        .order_by(sort_column.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    links = result.scalars().all()
    return links, total


async def increment_click_count(db: AsyncSession, link_id: UUID):
    """Atomically increment the click counter on a link (UPDATE SET click_count = click_count + 1)."""
    await db.execute(
        update(Link).where(Link.id == link_id).values(click_count=Link.click_count + 1)
    )
    await db.commit()


async def soft_delete_link(db: AsyncSession, link_id: UUID, user_id: UUID) -> bool:
    """Soft-delete a link by setting is_active=False. Data is preserved for analytics."""
    result = await db.execute(
        select(Link).where(Link.id == link_id, Link.user_id == user_id)
    )
    link = result.scalar_one_or_none()
    if not link:
        return False

    link.is_active = False
    await db.commit()
    return True
