from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Other
    CORS_ALLOWED_ORIGINS: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
