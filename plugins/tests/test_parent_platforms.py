from inspect import getattr_static

import pytest

from app.plugins.registry import plugin_registry
from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin
from app.technical_asset_configuration.service import PluginService

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
