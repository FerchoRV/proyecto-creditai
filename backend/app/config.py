from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(
        default="postgresql+psycopg2://creditai:creditai@db:5432/creditai",
        validation_alias="DATABASE_URL",
    )
    jwt_secret: str = Field(default="change-me-in-local-dev", validation_alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = Field(default=60 * 24, validation_alias="JWT_EXPIRE_MINUTES")


@lru_cache
def get_settings() -> Settings:
    return Settings()
