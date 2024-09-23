import json
from typing import Union
from uuid import UUID

from pydantic import field_validator

from app.environment_platform_service_configurations.glue_schema import AWSGlueConfig
from app.environment_platform_service_configurations.s3_schema import AWSS3Config
from app.environments.schema import Environment
from app.platform_services.schema import PlatformService
from app.platforms.schema import Platform
from app.shared.schema import ORMModel

configs = Union[AWSS3Config, AWSGlueConfig]


class EnvironmentPlatformServiceConfiguration(ORMModel):
    config: list[configs]
    id: UUID
    platform: Platform
    environment: Environment
    service: PlatformService

    @field_validator("config", mode="before")
    @classmethod
    def parse_settings(cls, v: str | list) -> list:
        if isinstance(v, str):
            return json.loads(v)
        return v
