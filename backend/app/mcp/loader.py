"""Registers MCP tools from every enabled technical asset plugin.

To add MCP tools for a plugin:
1. Override `register_mcp_tools(cls, mcp)` on the plugin class.
2. Set `mcp_instructions` on the class if needed.
"""

from fastmcp import FastMCP

from app.core.logging import logger
from app.plugins.registry import plugin_registry


def load_plugins(mcp: FastMCP) -> None:

    for plugin in plugin_registry.enabled():
        try:
            plugin.register_mcp_tools(mcp)
        except Exception:  # noqa: PERF203
            logger.exception(
                f"Plugin '{plugin.name}' failed to register MCP tools, skipping"
            )


def get_plugin_instructions() -> str:
    """Combine MCP instructions from all plugins that define them."""
    return "\n\n".join(
        plugin.mcp_instructions
        for plugin in plugin_registry.enabled()
        if plugin.mcp_instructions
    )
