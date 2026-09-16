from base64 import b64decode
from typing import ClassVar

from app.technical_asset_configuration.base_schema import (
    PlatformMetadata,
    TechnicalAssetPlugin,
)
from app.technical_asset_configuration.glue.schema import (
    GlueTechnicalAssetConfiguration,
)


class PluginWithBundledIcon(TechnicalAssetPlugin):
    name: ClassVar[str] = "PluginWithBundledIcon"
    configuration_type: str = "PluginWithBundledIcon"

    _platform_metadata = PlatformMetadata(
        display_name="Bundled icon",
        icon_name="icon.svg",
        icon_package="tests.fixtures.example_plugin",
        platform_key="bundled-icon-test",
        detailed_name="Bundled icon",
    )


def test_get_icon_data_uri__returns_none_when_no_package_is_declared():
    assert GlueTechnicalAssetConfiguration.get_icon_data_uri() is None


def test_get_icon_data_uri__encodes_the_icon_bundled_in_the_package():
    data_uri = PluginWithBundledIcon.get_icon_data_uri()

    assert data_uri.startswith("data:image/svg+xml;base64,")
    decoded = b64decode(data_uri.removeprefix("data:image/svg+xml;base64,"))
    assert decoded.startswith(b"<svg")
