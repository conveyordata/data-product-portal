import json
from uuid import UUID

from pydantic import Field, field_validator

from app.environment_platform_service_configurations.schemas import (
    AWSGlueConfig,
    AWSS3Config,
    DatabricksConfig,
)
from app.environments.schema import Environment
from app.platform_services.schema import PlatformService
from app.platforms.schema import Platform
from app.shared.schema import ORMModel

ConfigType = AWSS3Config | AWSGlueConfig | DatabricksConfig


class EnvironmentPlatformServiceConfiguration(ORMModel):
    config: list[ConfigType] = Field(
        ..., description="Configuration settings for the environment platform service"
    )
    id: UUID = Field(
        ...,
        description="Unique identifier of the env platform service configuration",
    )
    platform: Platform = Field(
        ...,
        description="Platform associated with the environment service configuration",
    )
    environment: Environment = Field(
        ...,
        description="Environment associated with the platform service configuration",
    )
    service: PlatformService = Field(
        ...,
        description="Service associated with the environment platform configuration",
    )

    @field_validator("config", mode="before")
    @classmethod
    def parse_settings(cls, v: str | list) -> list:
        if isinstance(v, str):
            return json.loads(v)
        return v
