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


@pytest.fixture
def no_entry_points(monkeypatch):
    monkeypatch.setattr("app.plugins.registry.entry_points", lambda group: [])


def test_discovered__loads_installed_plugins_from_entry_points(registry):
    """GitHub and S3 live outside the backend and are found only by entry point."""
    names = {plugin.name for plugin in registry.discovered()}

    assert "GitHubPlugin" in names
    assert "S3TechnicalAssetConfiguration" in names


def test_discovered__includes_in_tree_plugins(registry):
    names = {plugin.name for plugin in registry.discovered()}

    assert "GlueTechnicalAssetConfiguration" in names


def test_discovered__skips_entry_point_that_fails_to_import(registry, monkeypatch):
    monkeypatch.setattr(
        "app.plugins.registry.entry_points",
        lambda group: [_entry_point("broken", "no_such_module:Plugin")],
    )

    names = {plugin.name for plugin in registry.discovered()}

    assert "broken" not in names
    assert "GlueTechnicalAssetConfiguration" in names


def test_discovered__skips_entry_point_that_is_not_a_plugin(registry, monkeypatch):
    monkeypatch.setattr(
        "app.plugins.registry.entry_points",
        lambda group: [_entry_point("wrong", "json:JSONDecoder")],
    )

    names = {plugin.name for plugin in registry.discovered()}
    assert "wrong" not in names
    assert "JSONDecoder" not in names


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


def test_get__rejects_a_plugin_that_is_not_enabled(registry, monkeypatch):
    monkeypatch.setattr(settings, "ENABLED_PLUGINS", [])

    with pytest.raises(HTTPException) as exc_info:
        registry.get("S3TechnicalAssetConfiguration")

    assert exc_info.value.status_code == 400


def test_get__rejects_an_unknown_plugin(registry):
    with pytest.raises(HTTPException) as exc_info:
        registry.get("NoSuchPlugin")

    assert exc_info.value.status_code == 400
