from .config_schema import BaseEnvironmentPlatformServiceConfigurationDetail


class AWSGlueConfig(BaseEnvironmentPlatformServiceConfigurationDetail):
    database_name: str
    bucket_name: str
    s3_path: str
