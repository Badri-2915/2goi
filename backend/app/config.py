"""
Configuration Module — All application settings loaded from environment variables.

Uses Pydantic BaseSettings which automatically reads from:
1. Environment variables (highest priority)
2. .env file (for local development)
3. Default values defined here (lowest priority)

In production (Render), all values come from environment variables.
Locally, they come from backend/.env file.

The get_settings() function is cached with @lru_cache so the .env file
is only read once, not on every request.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ---- Database ----
    # Async driver for FastAPI (asyncpg)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/twogoi"
    # Sync driver for migrations and scripts (psycopg2)
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/twogoi"

    # ---- Supabase ----
    # Supabase project URL (used for auth, JWKS endpoint, etc.)
    SUPABASE_URL: str = ""
    # Service role key (admin access — NEVER expose in frontend)
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    # Anon key (public, safe for frontend — only allows RLS-restricted access)
    SUPABASE_ANON_KEY: str = ""
    # JWT secret (fallback for HS256 token verification)
    SUPABASE_JWT_SECRET: str = ""

    # ---- Redis ----
    # Redis URL for caching short link redirects
    REDIS_URL: str = "redis://localhost:6379/0"

    # ---- Application ----
    # Base URL used to construct short links (e.g., https://2goi.in/abc)
    BASE_URL: str = "https://2goi.in"
    # Frontend URL (same as BASE_URL in single-domain architecture)
    FRONTEND_URL: str = "https://app.2goi.in"
    # Environment: "development" or "production" (controls SQL logging, etc.)
    ENVIRONMENT: str = "development"

    # ---- Rate Limiting ----
    # Max requests per minute for anonymous users
    RATE_LIMIT_ANON: int = 100
    # Max requests per minute for authenticated users
    RATE_LIMIT_AUTH: int = 1000

    # ---- CORS ----
    # Comma-separated list of allowed origins (parsed in main.py)
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,https://app.2goi.in"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance (reads .env file only once)."""
    return Settings()
