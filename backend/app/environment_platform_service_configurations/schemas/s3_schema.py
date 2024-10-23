from .config_schema import BaseEnvironmentPlatformServiceConfigurationDetail


class AWSS3Config(BaseEnvironmentPlatformServiceConfigurationDetail):
    bucket_name: str
    bucket_arn: str
    kms_key_arn: str
    is_default: bool
