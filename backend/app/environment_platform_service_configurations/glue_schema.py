from app.environment_platform_service_configurations.config_schema import (
    BaseEnvironmentPlatformServiceConfigurationDetail,
)


class AWSGlueConfig(BaseEnvironmentPlatformServiceConfigurationDetail):
    database_name: str
    bucket_name: str
    s3_path: str
