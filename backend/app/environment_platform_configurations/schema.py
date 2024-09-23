import json
from typing import Union
from uuid import UUID

from pydantic import field_validator

from app.environment_platform_configurations.aws_schema import (
    AWSEnvironmentPlatformConfiguration,
)
from app.environments.schema import Environment
from app.platforms.schema import Platform
from app.shared.schema import ORMModel


class EnvironmentPlatformConfiguration(ORMModel):
    config: Union[AWSEnvironmentPlatformConfiguration]

    @field_validator("config", mode="before")
    @classmethod
    def parse_settings(cls, v: str | dict) -> dict:
        if isinstance(v, str):
            return json.loads(v)
        return v

    id: UUID
    environment: Environment
    platform: Platform
