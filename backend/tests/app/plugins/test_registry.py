from importlib.metadata import EntryPoint
from typing import ClassVar

import pytest
from fastapi import HTTPException

from app.plugins.registry import ENTRY_POINT_GROUP, PluginRegistry
from app.settings import settings
from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin


@pytest.fixture
def registry():
    return PluginRegistry()


def _entry_point(name: str, value: str) -> EntryPoint:
    return EntryPoint(name=name, value=value, group=ENTRY_POINT_GROUP)


GLUE = "app.technical_asset_configuration.glue.schema:GlueTechnicalAssetConfiguration"


def test_discovered__finds_the_plugins_this_package_advertises(registry):
    names = {plugin.name for plugin in registry.discovered()}

    assert "GlueTechnicalAssetConfiguration" in names
    assert "S3TechnicalAssetConfiguration" in names


def test_discovered__loads_only_what_the_entry_points_advertise(registry, monkeypatch):
    monkeypatch.setattr(
        "app.plugins.registry.entry_points",
        lambda group: [_entry_point("glue", GLUE)],
    )

    names = {plugin.name for plugin in registry.discovered()}

    assert names == {"GlueTechnicalAssetConfiguration"}


def test_discovered__rejects_a_plugin_that_declares_only_one_of_target_revision_or_migrations_package(
    registry, monkeypatch
):
    class HalfMigratedPlugin(TechnicalAssetPlugin):
        name: ClassVar[str] = "HalfMigratedPlugin"
        target_revision: ClassVar[str] = "some_revision"

    class FakeEntryPoint:
        def load(self) -> type[TechnicalAssetPlugin]:
            return HalfMigratedPlugin

    monkeypatch.setattr(
        "app.plugins.registry.entry_points",
        lambda group: [FakeEntryPoint()],
    )

    with pytest.raises(Exception, match="must declare both target_revision"):
        registry.discovered()


def test_enabled__excludes_a_plugin_that_is_installed_but_not_configured(
    registry, monkeypatch
):
    monkeypatch.setattr(
        settings, "ENABLED_PLUGINS", ["GlueTechnicalAssetConfiguration"]
    )

    names = {plugin.name for plugin in registry.enabled()}

    assert names == {"GlueTechnicalAssetConfiguration"}


def test_get__returns_an_enabled_plugin(registry):
    assert registry.get("S3TechnicalAssetConfiguration").name == (
        "S3TechnicalAssetConfiguration"
    )


def test_get__still_resolves_a_plugin_that_is_not_enabled(registry, monkeypatch):
    monkeypatch.setattr(settings, "ENABLED_PLUGINS", [])

    assert registry.get("S3TechnicalAssetConfiguration").name == (
        "S3TechnicalAssetConfiguration"
    )


def test_get__rejects_a_plugin_that_is_not_installed(registry):
    with pytest.raises(HTTPException) as exc_info:
        registry.get("NoSuchPlugin")

    assert exc_info.value.status_code == 400
