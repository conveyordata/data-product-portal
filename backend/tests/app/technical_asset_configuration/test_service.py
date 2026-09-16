from typing import ClassVar

from sqlalchemy.orm import Session

from app.technical_asset_configuration.base_schema import (
    PlatformMetadata,
    TechnicalAssetPlugin,
)
from app.technical_asset_configuration.glue.schema import (
    GlueTechnicalAssetConfiguration,
)
from app.technical_asset_configuration.service import PluginService


class PluginThatRaises(TechnicalAssetPlugin):
    name: ClassVar[str] = "PluginThatRaises"

    _platform_metadata = PlatformMetadata(
        display_name="Raises",
        icon_name="raises-logo.svg",
        platform_key="raises",
        detailed_name="Raises",
    )

    @classmethod
    def get_ui_metadata(cls, db: Session):
        raise RuntimeError("this plugin is broken")


def test_get_all_technical_assets_ui_metadata__drops_only_the_plugin_that_raises(
    session, monkeypatch
):
    monkeypatch.setattr(
        "app.technical_asset_configuration.service.plugin_registry.enabled",
        lambda: [PluginThatRaises, GlueTechnicalAssetConfiguration],
    )

    names = {
        m.plugin for m in PluginService(session).get_all_technical_assets_ui_metadata()
    }

    assert names == {"GlueTechnicalAssetConfiguration"}


def test_get_all_technical_assets_ui_metadata__logs_the_plugin_that_raised(
    session, monkeypatch
):
    logged = []
    monkeypatch.setattr(
        "app.technical_asset_configuration.service.logger.exception",
        lambda message: logged.append(message),
    )
    monkeypatch.setattr(
        "app.technical_asset_configuration.service.plugin_registry.enabled",
        lambda: [PluginThatRaises],
    )

    PluginService(session).get_all_technical_assets_ui_metadata()

    assert logged == ["Plugin 'PluginThatRaises' failed to describe its form, skipping"]
