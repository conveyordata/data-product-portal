from .config_schema import BaseEnvironmentPlatformServiceConfigurationDetail


class RedshiftConfig(BaseEnvironmentPlatformServiceConfigurationDetail):
    database_name: str
    bucket_identifier: str
    s3_path: str
