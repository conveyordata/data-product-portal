"""Registers MCP tools from every enabled technical asset plugin.

To add MCP tools for a plugin:
1. Override `register_mcp_tools(cls, mcp)` on the plugin class.
2. Set `mcp_instructions` on the class if needed.
"""

from typing import Sequence

from fastmcp import FastMCP

from app.plugins.registry import plugin_registry
from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin


def load_plugins(mcp: FastMCP) -> list[type[TechnicalAssetPlugin]]:
    registered = []
    for plugin in plugin_registry.enabled():
        plugin.register_mcp_tools(mcp)
        registered.append(plugin)
    return registered


def get_plugin_instructions(plugins: Sequence[type[TechnicalAssetPlugin]]) -> str:
    """Combine MCP instructions from plugins that registered successfully."""
    return "\n\n".join(
        plugin.mcp_instructions for plugin in plugins if plugin.mcp_instructions
    )
