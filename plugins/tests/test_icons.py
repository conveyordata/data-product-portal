import pytest

from app.plugins.registry import plugin_registry

PLUGINS = plugin_registry.discovered()


def test_discovered__finds_every_first_party_plugin():
    assert {plugin.name for plugin in PLUGINS} == {
        "AgnoPlugin",
        "AzureBlobTechnicalAssetConfiguration",
        "ConveyorPlugin",
        "DatabricksTechnicalAssetConfiguration",
        "GitHubPlugin",
        "GlueTechnicalAssetConfiguration",
        "OSISemanticModelTechnicalAssetConfiguration",
        "PostgreSQLTechnicalAssetConfiguration",
        "RedshiftTechnicalAssetConfiguration",
        "S3TechnicalAssetConfiguration",
        "SnowflakeTechnicalAssetConfiguration",
    }


@pytest.mark.parametrize("plugin", PLUGINS, ids=lambda plugin: plugin.name)
def test_get_icon_data_uri__reads_the_icon_from_the_plugins_own_package(plugin):
    metadata = plugin.get_platform_metadata()

    assert metadata.icon_package == plugin.__module__.rsplit(".", 1)[0]
    assert plugin.get_icon_data_uri().startswith("data:image/svg+xml;base64,")
