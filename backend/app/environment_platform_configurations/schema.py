import json
from typing import Union
from uuid import UUID

from pydantic import Field, field_validator

from app.environment_platform_configurations.schemas import (
    AWSEnvironmentPlatformConfiguration,
    DatabricksEnvironmentPlatformConfiguration,
)
from app.environments.schema import Environment
from app.platforms.schema import Platform
from app.shared.schema import ORMModel


class EnvironmentPlatformConfiguration(ORMModel):
    config: Union[
        AWSEnvironmentPlatformConfiguration, DatabricksEnvironmentPlatformConfiguration
    ] = Field(..., description="Configuration settings for the environment platform")

    @field_validator("config", mode="before")
    @classmethod
    def parse_settings(cls, v: str | dict) -> dict:
        if isinstance(v, str):
            return json.loads(v)
        return v

    id: UUID = Field(
        ..., description="Unique identifier for the environment platform configuration"
    )
    environment: Environment = Field(
        ..., description="Environment associated with the platform configuration"
    )
    platform: Platform = Field(
        ..., description="Platform associated with the environment configuration"
    )
