from typing import ClassVar

import pytest
from fastmcp import FastMCP

from app.mcp.loader import get_plugin_instructions, load_plugins
from app.plugins.registry import PluginRegistry
from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin


class BrokenPlugin(TechnicalAssetPlugin):
    name: ClassVar[str] = "BrokenPlugin"

    @classmethod
    def register_mcp_tools(cls, mcp) -> None:
        raise RuntimeError("this plugin is broken")


class WorkingPlugin(TechnicalAssetPlugin):
    name: ClassVar[str] = "WorkingPlugin"
    mcp_instructions: ClassVar[str] = "working plugin instructions"

    registered: ClassVar[bool] = False

    @classmethod
    def register_mcp_tools(cls, mcp) -> None:
        cls.registered = True


def test_load_plugins__registers_every_enabled_plugin(monkeypatch):
    WorkingPlugin.registered = False
    monkeypatch.setattr(
        "app.mcp.loader.plugin_registry.enabled", lambda: [WorkingPlugin]
    )

    registered = load_plugins(mcp=None)

    assert WorkingPlugin.registered
    assert registered == [WorkingPlugin]


def test_load_plugins__propagates_a_plugins_exception(monkeypatch):
    monkeypatch.setattr(
        "app.mcp.loader.plugin_registry.enabled",
        lambda: [BrokenPlugin, WorkingPlugin],
    )

    with pytest.raises(RuntimeError, match="this plugin is broken"):
        load_plugins(mcp=None)


def test_get_plugin_instructions__joins_instructions_from_plugins_that_declare_them():
    class NoInstructionsPlugin(TechnicalAssetPlugin):
        name: ClassVar[str] = "NoInstructionsPlugin"

    assert (
        get_plugin_instructions([WorkingPlugin, NoInstructionsPlugin])
        == "working plugin instructions"
    )


def test_register_mcp_tools__every_discovered_plugin_registers_without_raising():
    mcp = FastMCP()

    for plugin in PluginRegistry().discovered():
        plugin.register_mcp_tools(mcp)
