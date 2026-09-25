from typing import ClassVar

from fastmcp import FastMCP

from app.mcp.loader import get_plugin_instructions, load_plugins
from app.plugins.registry import PluginRegistry
from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin


class BrokenPlugin(TechnicalAssetPlugin):
    name: ClassVar[str] = "BrokenPlugin"
    mcp_instructions: ClassVar[str] = "do not show this"

    @classmethod
    def register_mcp_tools(cls, mcp) -> None:
        raise RuntimeError("this plugin is broken")


class WorkingPlugin(TechnicalAssetPlugin):
    name: ClassVar[str] = "WorkingPlugin"

    registered: ClassVar[bool] = False

    @classmethod
    def register_mcp_tools(cls, mcp) -> None:
        cls.registered = True


def test_load_plugins__keeps_going_when_a_plugin_raises(monkeypatch):
    WorkingPlugin.registered = False
    monkeypatch.setattr(
        "app.mcp.loader.plugin_registry.enabled",
        lambda: [BrokenPlugin, WorkingPlugin],
    )

    load_plugins(mcp=None)

    assert WorkingPlugin.registered


def test_load_plugins__excludes_a_plugin_that_raised_from_the_returned_list(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.mcp.loader.plugin_registry.enabled",
        lambda: [BrokenPlugin, WorkingPlugin],
    )

    registered = load_plugins(mcp=None)

    assert registered == [WorkingPlugin]


def test_get_plugin_instructions__omits_a_plugin_that_failed_to_register(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.mcp.loader.plugin_registry.enabled", lambda: [BrokenPlugin]
    )

    registered = load_plugins(mcp=None)

    assert get_plugin_instructions(registered) == ""


def test_load_plugins__logs_the_plugin_that_failed(monkeypatch):
    logged = []
    monkeypatch.setattr(
        "app.mcp.loader.logger.exception", lambda message: logged.append(message)
    )
    monkeypatch.setattr(
        "app.mcp.loader.plugin_registry.enabled", lambda: [BrokenPlugin]
    )

    load_plugins(mcp=None)

    assert logged == ["Plugin 'BrokenPlugin' failed to register MCP tools, skipping"]


def test_register_mcp_tools__every_discovered_plugin_registers_without_raising():
    mcp = FastMCP()

    for plugin in PluginRegistry().discovered():
        plugin.register_mcp_tools(mcp)
