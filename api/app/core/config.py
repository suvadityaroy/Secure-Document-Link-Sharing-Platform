"""Configuration management for FastAPI application."""
import os
from typing import Optional
from datetime import timedelta
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./document_sharing.db"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # JWT
    JWT_SECRET: str = os.getenv(
        "JWT_SECRET",
        "your-secret-key-change-in-production-minimum-32-chars"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # File Service
    FILE_SERVICE_URL: str = os.getenv(
        "FILE_SERVICE_URL",
        "http://localhost:8081"
    )
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS - Allow frontend origins
    # Exact origins that are always allowed
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    # Regex for public hosting providers (subdomains)
    ALLOWED_ORIGIN_REGEX: str = (
        os.getenv(
            "ALLOWED_ORIGIN_REGEX",
            r"^https?://([a-zA-Z0-9-]+\.)*vercel\.app$|^https?://([a-zA-Z0-9-]+\.)*netlify\.app$|^https?://([a-zA-Z0-9-]+\.)*railway\.app$|^http://localhost(:\d+)?$"
        )
    )
    # Set to true to allow all origins (useful for quick demos)
    ALLOW_ALL_CORS: bool = os.getenv("ALLOW_ALL_CORS", "false").lower() == "true"

    # Optional: Public frontend URL. If set, API root will redirect here.
    FRONTEND_URL: Optional[str] = os.getenv("FRONTEND_URL")
    
    # API
    API_TITLE: str = "Secure Document & Link Sharing Platform"
    API_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
