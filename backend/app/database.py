"""
Database Module — Async SQLAlchemy engine and session management.

This module sets up:
1. Async database engine (asyncpg driver for PostgreSQL)
2. Session factory for creating database sessions per request
3. Base class for all SQLAlchemy models
4. Dependency function for FastAPI's dependency injection

Connection details:
- Uses Supabase's session pooler (not direct connection, because Supabase is IPv6-only)
- SSL is required for Supabase connections
- Connection pool: 20 connections + 10 overflow, recycled every 5 minutes
- pool_pre_ping=True ensures dead connections are detected and replaced
"""

import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()

# SSL context for Supabase pooler connection
# verify_mode=CERT_NONE because Supabase pooler uses its own certificate
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Create async database engine with connection pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",  # Log SQL queries in development
    pool_size=20,       # Max 20 persistent connections
    max_overflow=10,    # Allow 10 extra connections under load
    pool_pre_ping=True, # Check if connection is alive before using it
    pool_recycle=300,   # Recycle connections every 5 minutes (avoids stale connections)
    connect_args={"ssl": ssl_context},
)

# Session factory — creates a new AsyncSession for each request
# expire_on_commit=False means objects remain usable after commit
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models. All models inherit from this."""
    pass


async def get_db() -> AsyncSession:
    """
    FastAPI dependency that provides a database session per request.
    The session is automatically closed when the request finishes.
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
