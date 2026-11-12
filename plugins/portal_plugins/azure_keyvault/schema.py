import re
from typing import Any, ClassVar

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.technical_asset_configuration.base_schema import (
    PlatformMetadata,
    PluginContext,
    TechnicalAssetPlugin,
)
from portal_plugins.azure_keyvault.model import NAME
from portal_plugins.azure_keyvault.model import (
    AzureKeyVaultTechnicalAssetConfiguration as AzureKeyVaultTechnicalAssetConfigurationModel,
)
from portal_plugins.common.azure_helpers import get_azure_plugin_url

KEY_VAULT_PREFIX = "kv-adp-"
KEY_VAULT_MAX_LENGTH = 20
KEY_VAULT_NAME_PATTERN = re.compile(r"^[a-z0-9-]+$")


class AzureKeyVaultTechnicalAssetConfiguration(TechnicalAssetPlugin):
    name: ClassVar[str] = NAME
    version: ClassVar[str] = "1.0"

    vault_name: str = ""

    _platform_metadata = PlatformMetadata(
        result_string_template="{vault_name}",
        technical_info_template="https://{vault_name}-{environment}.vault.azure.net/",
        display_name="Key Vault",
        icon_name="azure-keyvault-logo.svg",
        icon_package="portal_plugins.azure_keyvault",
        platform_key="azurekeyvault",
        parent_platform="azure",
        result_label="Resulting Key Vault",
        result_tooltip="The Key Vault created for this Technical Asset",
        detailed_name="Key Vault",
    )

    class Meta:
        orm_model = AzureKeyVaultTechnicalAssetConfigurationModel

    def render_template(
        self, template: str, *, plugin_context: PluginContext, **context: Any
    ) -> str:
        if plugin_context.technical_asset.id is None:
            context["vault_name"] = (
                f"{KEY_VAULT_PREFIX}{plugin_context.technical_asset.name}"
            )
        elif not self.vault_name:
            raise ValueError("Key Vault configuration is missing its stored vault name")
        else:
            context["vault_name"] = self.vault_name
        return super().render_template(
            template,
            plugin_context=plugin_context,
            **context,
        )

    def validate_configuration(self, context: PluginContext, db: Session) -> None:
        name = context.technical_asset.name
        key_vault_name = f"{KEY_VAULT_PREFIX}{name}"

        if not name:
            raise ValueError("Key Vault must include a name")
        if len(key_vault_name) > KEY_VAULT_MAX_LENGTH:
            raise ValueError(
                "Key Vault name must be maximum 20 characters long, including kv-adp-"
            )
        if not KEY_VAULT_NAME_PATTERN.fullmatch(key_vault_name):
            raise ValueError(
                "Key Vault name can only contain lowercase letters, numbers, and hyphens"
            )
        if "--" in key_vault_name:
            raise ValueError("Key Vault name cannot contain consecutive hyphens")
        if db.scalar(
            select(
                exists().where(
                    AzureKeyVaultTechnicalAssetConfigurationModel.vault_name
                    == key_vault_name,
                )
            )
        ):
            raise ValueError(f"Key Vault {key_vault_name} already exists")
        self.vault_name = key_vault_name

    get_url = classmethod(get_azure_plugin_url)

    def get_configuration(self, configs: list) -> None:
        return None
