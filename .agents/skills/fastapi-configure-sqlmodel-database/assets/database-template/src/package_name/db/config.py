import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


APP_ENV = os.getenv("APP_ENV", "development")


class DatabaseSettings(BaseSettings):
    database_url: str
    db_echo: bool = False

    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{APP_ENV}"),
        extra="ignore",
    )


@lru_cache
def get_settings() -> DatabaseSettings:
    return DatabaseSettings()

