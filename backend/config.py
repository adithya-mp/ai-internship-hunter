"""
ApplyIQ Backend Configuration
Reads environment variables using Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ─── Database ───
    DATABASE_URL: str = "sqlite+aiosqlite:///./applyiq.db"

    # ─── Redis ───
    REDIS_URL: str = "redis://redis:6379/0"

    # ─── JWT Auth ───
    JWT_SECRET_KEY: str = "change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    # ─── Gemini AI ───
    GEMINI_API_KEY: str = ""

    # ─── App ───
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:5173"
    ENVIRONMENT: str = "development"

    # ─── Scraping ───
    SCRAPE_INTERVAL_HOURS: int = 6

    # ─── Uploads ───
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    class Config:
        env_file = (".env", "../.env")
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
