import json
from typing import Sequence
from uuid import UUID

from pydantic import field_validator

from app.configuration.environments.platform_service_configurations.schemas import (
    AWSGlueConfig,
    AWSS3Config,
    DatabricksConfig,
    PostgresConfig,
)
from app.configuration.environments.platform_service_configurations.schemas.redshift_schema import (
    RedshiftConfig,
)
from app.configuration.environments.platform_service_configurations.schemas.snowflake_schema import (
    SnowflakeConfig,
)
from app.configuration.environments.schema_response import Environment
from app.configuration.platforms.platform_services.schema import PlatformService
from app.configuration.platforms.schema_response import Platform
from app.shared.schema import ORMModel

ConfigType = (
    AWSS3Config
    | AWSGlueConfig
    | DatabricksConfig
    | SnowflakeConfig
    | PostgresConfig
    | RedshiftConfig
)


class EnvironmentConfigsGetItem(ORMModel):
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


class EnvironmentConfigsGet(ORMModel):
    environment_configs: Sequence[EnvironmentConfigsGetItem]
