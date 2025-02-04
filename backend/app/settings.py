from enum import Enum
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_SERVER: str

    HOST: str

    # Other
    CORS_ALLOWED_ORIGINS: str = ""
    AWS_DEFAULT_REGION: str = "eu-west-1"
    AWS_DEFAULT_PROFILE: Optional[str] = None
    PORTAL_API_KEY: Optional[str] = None

    # OIDC Configuration
    OIDC_ENABLED: bool = False
    OIDC_CLIENT_ID: Optional[str] = None
    OIDC_CLIENT_SECRET: Optional[str] = None
    OIDC_AUTHORITY: Optional[str] = None
    OIDC_REDIRECT_URI: Optional[str] = None

    # Conveyor
    CONVEYOR_API_KEY: Optional[str] = None
    CONVEYOR_SECRET: Optional[str] = None

    # Infrastructure
    INFRASTRUCTURE_LAMBDA_ARN: Optional[str] = None
    WEBHOOK_URL: Optional[str] = None
    ENVIRONMENT_CONTEXT: Optional[str] = None

    # Email templating and SMTP settings
    PORTAL_NAME: str = "Data Product Portal"
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_NO_LOGIN: bool = False
    SMTP_USERNAME: str = "admin"
    SMTP_PASSWORD: str = "not-set"
    FROM_MAIL_ADDRESS: str = "noreply@dataproductportal.com"
    CORPORATION: str = "Dataminded"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggerConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    LOG_LEVEL: LogLevel = LogLevel.INFO
    LOG_CONFIG_FILE: str = "log_config.json"
    LOGGING_DIRECTORY: str = "/var/logs"
    SCARF_NO_ANALYTICS: bool = False
    DO_NOT_TRACK: bool = False
    SANDBOX: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
