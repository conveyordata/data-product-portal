import json
from typing import Union
from uuid import UUID

from pydantic import field_validator

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
    ]

    @field_validator("config", mode="before")
    @classmethod
    def parse_settings(cls, v: str | dict) -> dict:
        if isinstance(v, str):
            return json.loads(v)
        return v

    id: UUID
    environment: Environment
    platform: Platform
