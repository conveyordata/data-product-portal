from .config_schema import BaseEnvironmentPlatformServiceConfigurationDetail


class AzureBlobConfig(BaseEnvironmentPlatformServiceConfigurationDetail):
    storage_account_name: str
    resource_group_name: str
    container_name: str
