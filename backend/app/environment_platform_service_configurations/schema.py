import json
from uuid import UUID

from pydantic import field_validator

from app.environment_platform_service_configurations.schemas import (
    AWSGlueConfig,
    AWSS3Config,
    DatabricksConfig,
)
from app.environment_platform_service_configurations.schemas.redshift_schema import (
    RedshiftConfig,
)
from app.environment_platform_service_configurations.schemas.snowflake_schema import (
    SnowflakeConfig,
)
from app.environments.schema import Environment
from app.platform_services.schema import PlatformService
from app.platforms.schema import Platform
from app.shared.schema import ORMModel

ConfigType = (
    AWSS3Config | AWSGlueConfig | DatabricksConfig | SnowflakeConfig | RedshiftConfig
)


class EnvironmentPlatformServiceConfiguration(ORMModel):
    config: list[ConfigType]
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
