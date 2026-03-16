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

# Base62 alphabet: 0-9, a-z, A-Z (62 chars → supports 62^6 = 56B+ unique codes)
BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def encode_base62(num: int) -> str:
    """Encode an integer to a Base62 string. Used with sequential DB IDs to
    generate collision-free short codes without any duplicate checks."""
    if num == 0:
        return BASE62_ALPHABET[0]
    base = len(BASE62_ALPHABET)
    encoded = []
    while num:
        num, rem = divmod(num, base)
        encoded.append(BASE62_ALPHABET[rem])
    return ''.join(reversed(encoded))


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

    expires_at = None
    if expires_in:
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    # Insert with a temporary short_code (will be replaced by Base62-encoded sequence_id)
    link = Link(
        original_url=original_url,
        short_code=custom_alias or "__pending__",
        user_id=user_id,
        click_count=0,
        is_active=True,
        expires_at=expires_at,
    )

    db.add(link)
    await db.flush()  # Flush to get the DB-generated sequence_id

    # If no custom alias, generate short_code from sequential ID via Base62
    if not custom_alias:
        link.short_code = encode_base62(link.sequence_id)

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
