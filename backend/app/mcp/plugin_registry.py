"""Plugin registry interface for MCP tool providers.

Each data_output_configuration plugin that wants to expose MCP tools implements
MCPPlugin in a `mcp_tools.py` module within its own directory, then registers
itself in `app/mcp/loader.py`.
"""

from abc import ABC, abstractmethod

from fastmcp import FastMCP


class MCPPlugin(ABC):
    """Base class for data output configuration plugins that expose MCP tools.

    Implement this in `app/technical_asset_configuration/<plugin>/mcp_tools.py`.
    Register the implementation in `app/mcp/loader.py`.
    """

    @property
    def instructions(self) -> str:
        """Additional AI client instructions for this plugin's tools.

        Override to provide guidance on how to use the plugin's tools.
        The text is appended to the MCP server's base instructions.
        """
        return ""

    @abstractmethod
    def register_tools(self, mcp: FastMCP) -> None:
        """Register all plugin-specific MCP tools with the server."""
        ...
