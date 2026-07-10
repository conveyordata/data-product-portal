"""Plugin loader: auto-discovers and registers all MCP plugin tools.

To add a new plugin:
1. Create `app/data_output_configuration/<name>/mcp_tools.py`.
2. Implement `MCPPlugin` in that module.
3. That's it — no changes needed here.
"""

import importlib
from pathlib import Path

from fastmcp import FastMCP

from app.core.logging import logger
from app.mcp.plugin_registry import MCPPlugin


def _import_plugin_modules() -> None:
    """Import every mcp_tools.py found under data_output_configuration/.

    Importing a module that defines an MCPPlugin subclass registers that
    subclass via Python's normal class machinery, so MCPPlugin.__subclasses__()
    will include it afterwards.
    """
    base_path = Path(__file__).parent.parent / "data_output_configuration"
    base_package = "app.data_output_configuration"

    for directory in sorted(base_path.iterdir()):
        module_file = directory / "mcp_tools.py"
        if not (directory.is_dir() and module_file.exists()):
            continue
        module_name = f"{base_package}.{directory.name}.mcp_tools"
        try:
            importlib.import_module(module_name)
            logger.debug(f"[MCP] Loaded plugin module: {module_name}")
        except ImportError as exc:
            logger.warning(f"[MCP] Skipping plugin {module_name}: {exc}")


def _build_plugins() -> list[MCPPlugin]:
    """Import all plugin modules and return one instance of each MCPPlugin subclass."""
    _import_plugin_modules()
    return [cls() for cls in MCPPlugin.__subclasses__()]  # type: ignore[abstract]


PLUGINS: list[MCPPlugin] = _build_plugins()


def load_plugins(mcp: FastMCP) -> None:
    """Register all discovered plugin tools with the MCP server."""
    for plugin in PLUGINS:
        plugin.register_tools(mcp)


def get_plugin_instructions() -> str:
    """Combine additional instructions from all active plugins."""
    return "\n\n".join(p.instructions for p in PLUGINS if p.instructions)
