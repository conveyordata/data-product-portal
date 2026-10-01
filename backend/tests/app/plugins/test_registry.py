from importlib.metadata import EntryPoint

import pytest
from fastapi import HTTPException

from app.plugins.registry import ENTRY_POINT_GROUP, PluginRegistry
from app.settings import settings


@pytest.fixture
def registry():
    return PluginRegistry()


def _entry_point(name: str, value: str) -> EntryPoint:
    return EntryPoint(name=name, value=value, group=ENTRY_POINT_GROUP)


FAKE = "tests.fixtures.fake_plugin.schema:FakeTechnicalAssetConfiguration"


def test_discovered__finds_the_plugins_this_package_advertises(registry):
    names = {plugin.name for plugin in registry.discovered()}

    assert "FakeTechnicalAssetConfiguration" in names
    assert "FakeLinkPlugin" in names


def test_discovered__loads_only_what_the_entry_points_advertise(registry, monkeypatch):
    monkeypatch.setattr(
        "app.plugins.registry.entry_points",
        lambda group: [_entry_point("fake", FAKE)],
    )

    names = {plugin.name for plugin in registry.discovered()}

    assert names == {"FakeTechnicalAssetConfiguration"}


def test_enabled__excludes_a_plugin_that_is_installed_but_not_configured(
    registry, monkeypatch
):
    monkeypatch.setattr(settings, "ENABLED_PLUGINS", ["FakeLinkPlugin"])

    names = {plugin.name for plugin in registry.enabled()}

    assert names == {"FakeLinkPlugin"}


def test_get__returns_an_enabled_plugin(registry):
    assert registry.get("FakeLinkPlugin").name == "FakeLinkPlugin"


def test_get__still_resolves_a_plugin_that_is_not_enabled(registry, monkeypatch):
    monkeypatch.setattr(settings, "ENABLED_PLUGINS", [])

    assert registry.get("FakeLinkPlugin").name == "FakeLinkPlugin"


def test_get__rejects_a_plugin_that_is_not_installed(registry):
    with pytest.raises(HTTPException) as exc_info:
        registry.get("NoSuchPlugin")

    assert exc_info.value.status_code == 400
