from pydantic import ConfigDict

from app.environment_platform_service_configurations.schemas.config_schema import (
    BaseEnvironmentPlatformServiceConfigurationDetail,
)


class DatabricksConfig(BaseEnvironmentPlatformServiceConfigurationDetail):
    model_config = ConfigDict(extra="forbid")
