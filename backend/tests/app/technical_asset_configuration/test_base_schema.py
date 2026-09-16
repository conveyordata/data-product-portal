from base64 import b64decode
from typing import ClassVar

from app.technical_asset_configuration.base_schema import (
    PlatformMetadata,
    TechnicalAssetPlugin,
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


def test_get_icon_data_uri__encodes_the_icon_bundled_in_the_package():
    data_uri = PluginWithBundledIcon.get_icon_data_uri()

    assert data_uri.startswith("data:image/svg+xml;base64,")
    decoded = b64decode(data_uri.removeprefix("data:image/svg+xml;base64,"))
    assert decoded.startswith(b"<svg")


class PluginWithBrokenIcon(TechnicalAssetPlugin):
    name: ClassVar[str] = "PluginWithBrokenIcon"

    _platform_metadata = PlatformMetadata(
        display_name="Broken icon",
        icon_name="does-not-exist.svg",
        icon_package="tests.fixtures.example_plugin",
        platform_key="broken-icon-test",
        detailed_name="Broken icon",
    )


def test_get_icon_data_uri__returns_none_when_the_icon_cannot_be_read():
    assert PluginWithBrokenIcon.get_icon_data_uri() is None
