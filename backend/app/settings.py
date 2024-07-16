from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_SERVER: str

    # Other
    CORS_ALLOWED_ORIGINS: str = ""
    AWS_DEFAULT_REGION: str = "eu-west-1"

    # OIDC Configuration
    OIDC_DISABLED: bool = True

    # Conveyor
    CONVEYOR_API_KEY: Optional[str] = None
    CONVEYOR_SECRET: Optional[str] = None
    LOGGING_DIRECTORY: str = "./tmp/logs"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
