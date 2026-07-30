"""Application Settings Module.

Uses Pydantic v2 BaseSettings to parse environment variables with type validation.
"""

from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Production application settings loaded from environment or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    PROJECT_NAME: str = "FirstAid+ API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Database connection string (defaults to SQLite async for immediate local zero-config run)
    DATABASE_URL: str = "sqlite+aiosqlite:///./health_triage.db"

    # JWT & Auth
    JWT_SECRET_KEY: str = "development-secret-jwt-key-safe-for-local-testing"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # External AI
    GEMINI_API_KEY: str = "mock-dev-gemini-key"

    # CORS origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parses CORS origins string or list into a validated list of strings."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v

    from pydantic import model_validator
    @model_validator(mode="after")
    def validate_production_secrets(self) -> 'Settings':
        if self.ENVIRONMENT.lower() == "production":
            if self.JWT_SECRET_KEY == "development-secret-jwt-key-safe-for-local-testing":
                raise ValueError("JWT_SECRET_KEY must be overridden in production!")
            if len(self.JWT_SECRET_KEY) < 32:
                raise ValueError("JWT_SECRET_KEY must be at least 32 characters long in production.")
        return self


settings = Settings()
