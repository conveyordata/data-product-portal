from .config_schema import BaseEnvironmentPlatformServiceConfigurationDetail


class AzureBlobConfig(BaseEnvironmentPlatformServiceConfigurationDetail):
    storage_account_names: dict[
        str, str
    ]  # Support mapping of domains to storage accounts or just use default if there is only 1
