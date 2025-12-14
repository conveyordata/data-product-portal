from .config_schema import BaseEnvironmentPlatformServiceConfigurationDetail


class PostgreSQLConfig(BaseEnvironmentPlatformServiceConfigurationDetail):
    database_name: str
