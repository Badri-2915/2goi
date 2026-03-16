import string
import random
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

BASE62_CHARS = string.ascii_letters + string.digits


def generate_short_code(length: int = 5) -> str:
    return ''.join(random.choices(BASE62_CHARS, k=length))


def generate_qr_code(url: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def hash_ip(ip: str) -> str:
    return hashlib.sha256(ip.encode()).hexdigest()


async def create_short_link(
    db: AsyncSession,
    original_url: str,
    custom_alias: Optional[str] = None,
    expires_in: Optional[int] = None,
    user_id: Optional[UUID] = None,
) -> Link:
    if custom_alias:
        existing = await db.execute(
            select(Link).where(Link.short_code == custom_alias)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Custom alias '{custom_alias}' is already taken")
        short_code = custom_alias
    else:
        # Generate unique code with collision retry
        for _ in range(10):
            short_code = generate_short_code()
            existing = await db.execute(
                select(Link).where(Link.short_code == short_code)
            )
            if not existing.scalar_one_or_none():
                break
        else:
            raise ValueError("Failed to generate unique short code. Please try again.")

    expires_at = None
    if expires_in:
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    link = Link(
        original_url=original_url,
        short_code=short_code,
        user_id=user_id,
        click_count=0,
        is_active=True,
        expires_at=expires_at,
    )

    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


async def get_link_by_code(db: AsyncSession, short_code: str) -> Optional[Link]:
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
    await db.execute(
        update(Link).where(Link.id == link_id).values(click_count=Link.click_count + 1)
    )
    await db.commit()


async def soft_delete_link(db: AsyncSession, link_id: UUID, user_id: UUID) -> bool:
    result = await db.execute(
        select(Link).where(Link.id == link_id, Link.user_id == user_id)
    )
    link = result.scalar_one_or_none()
    if not link:
        return False

    link.is_active = False
    await db.commit()
    return True
