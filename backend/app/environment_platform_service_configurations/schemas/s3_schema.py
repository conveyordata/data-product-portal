from .config_schema import BaseEnvironmentPlatformServiceConfigurationDetail


class AWSS3Config(BaseEnvironmentPlatformServiceConfigurationDetail):
    bucket_name: str
    arn: str
    kms_key: str
    is_default: bool
