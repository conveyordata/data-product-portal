import json
from typing import Union
from uuid import UUID

from pydantic import field_validator

from app.configuration.environments.platform_configurations.schemas import (
    AWSEnvironmentPlatformConfiguration,
    DatabricksEnvironmentPlatformConfiguration,
)
from app.configuration.environments.schema_response import Environment
from app.configuration.platforms.schema_response import Platform
from app.shared.schema import ORMModel


class EnvironmentPlatformConfigGet(ORMModel):
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
