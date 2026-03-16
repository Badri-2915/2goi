from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/twogoi"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/twogoi"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # App
    BASE_URL: str = "https://2goi.in"
    FRONTEND_URL: str = "https://app.2goi.in"
    ENVIRONMENT: str = "development"

    # Rate Limiting
    RATE_LIMIT_ANON: int = 100
    RATE_LIMIT_AUTH: int = 1000

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,https://app.2goi.in"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
