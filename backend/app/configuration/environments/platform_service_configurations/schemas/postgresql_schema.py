from .config_schema import BaseEnvironmentPlatformServiceConfigurationDetail


class PostgreSQLConfig(BaseEnvironmentPlatformServiceConfigurationDetail):
    host: str
    port: str
    admin_user: str
    admin_pwd: str
