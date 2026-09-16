from typing import ClassVar

from app.mcp.loader import load_plugins
from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin


class BrokenPlugin(TechnicalAssetPlugin):
    name: ClassVar[str] = "BrokenPlugin"

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
