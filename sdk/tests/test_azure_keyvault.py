from sdk.api_client.models.get_technical_assets_response_item_configuration import (
    GetTechnicalAssetsResponseItemConfiguration,
)
from sdk.plugins.azure_keyvault import AzureKeyVaultTechnicalAssetConfiguration


def test_from_configuration__preserves_stored_vault_name():
    payload = {
        "name": "AzureKeyVaultTechnicalAssetConfiguration",
        "vault_name": "kv-adp-copilot-usage",
    }
    response = GetTechnicalAssetsResponseItemConfiguration.from_dict(payload)

    configuration = AzureKeyVaultTechnicalAssetConfiguration.from_configuration(
        response
    )

    assert configuration is not None
    assert configuration.to_dict() == payload
