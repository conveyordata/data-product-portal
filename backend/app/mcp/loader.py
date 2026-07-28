"""Plugin loader: registers MCP tools from all AssetProviderPlugin subclasses.

To add MCP tools for a new plugin:
1. Override `register_mcp_tools(cls, mcp)` in the plugin's AssetProviderPlugin subclass.
2. Set `mcp_instructions` on the class if needed.
3. That's it — no changes needed here.
"""

from typing import get_args

from fastmcp import FastMCP

from app.technical_asset_configuration.schema_union import DataOutputs


def load_plugins(mcp: FastMCP) -> None:
    """Register MCP tools from all AssetProviderPlugin subclasses."""
    for cls in get_args(DataOutputs):
        cls.register_mcp_tools(mcp)


def get_plugin_instructions() -> str:
    """Combine MCP instructions from all plugins that define them."""
    return "\n\n".join(
        cls.mcp_instructions for cls in get_args(DataOutputs) if cls.mcp_instructions
    )
