from inspect import getattr_static
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.plugins.registry import plugin_registry
from app.core.azure.get_url import get_azure_plugin_url
from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin
from app.technical_asset_configuration.service import PluginService
from portal_plugins.azure_blob.schema import AzureBlobTechnicalAssetConfiguration

PLUGINS = plugin_registry.discovered()
PARENT_PLATFORMS = sorted(
    {
        parent
        for plugin in PLUGINS
        if (parent := plugin.get_platform_metadata().parent_platform)
    }
)


@pytest.mark.parametrize("parent_platform", PARENT_PLATFORMS)
def test_parent_platform_url_plugin__children_share_one_get_url(parent_platform):
    plugin = PluginService._parent_platform_url_plugin(parent_platform, PLUGINS)

    assert plugin is not None
    assert (
        getattr_static(plugin, "get_url").__func__
        is not getattr_static(TechnicalAssetPlugin, "get_url").__func__
    )


def test_parent_platform_url_plugin__supports_custom_azure_child():
    class CustomAzurePlugin(TechnicalAssetPlugin):
        _platform_metadata = (
            AzureBlobTechnicalAssetConfiguration.get_platform_metadata().model_copy(
                update={"platform_key": "custom-azure"}
            )
        )
        get_url = classmethod(get_azure_plugin_url)

    plugin = PluginService._parent_platform_url_plugin(
        "azure", [AzureBlobTechnicalAssetConfiguration, CustomAzurePlugin]
    )

    assert plugin is not None
    assert plugin.get_url(uuid4(), Mock(), actor=Mock()) == "https://portal.azure.com/"
