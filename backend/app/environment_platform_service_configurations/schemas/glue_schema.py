from .config_schema import BaseEnvironmentPlatformServiceConfigurationDetail


class AWSGlueConfig(BaseEnvironmentPlatformServiceConfigurationDetail):
    glue_database_name: str
    bucket_identifier: str
    s3_path: str
