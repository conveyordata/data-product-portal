from functools import lru_cache

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_SERVER: str

    # Other
    CORS_ALLOWED_ORIGINS: list[HttpUrl] = [
        "http://localhost:3000",
        "http://localhost:5050",
        "http://localhost:8080",
    ]
    AWS_DEFAULT_REGION: str = "eu-west-1"

    # OIDC Configuration
    OIDC_DISABLED: bool = True

    # Conveyor
    CONVEYOR_API_KEY: str
    CONVEYOR_SECRET: str
    LOGGING_DIRECTORY: str = "./tmp/logs"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
