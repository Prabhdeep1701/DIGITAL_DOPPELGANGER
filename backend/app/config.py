from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/doppelganger"
    SYNC_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/doppelganger"
    CORS_ORIGINS: str = "http://localhost:3000"
    SECRET_KEY: str = "change-me-in-production"
    DEBUG: bool = True

    @property
    def async_database_url(self) -> str:
        """Ensure the DATABASE_URL uses the asyncpg driver."""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()
