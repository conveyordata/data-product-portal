from .config_schema import BaseEnvironmentPlatformServiceConfigurationDetail


class SnowflakeConfig(BaseEnvironmentPlatformServiceConfigurationDetail):
    database_name: str
