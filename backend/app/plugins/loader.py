"""Discovers technical asset plugins via Python entry points.

Plain `importlib.metadata.entry_points` - not `pluggy`. Installing a plugin
package is enough; nothing is named in a settings file. See ADR-0024.
"""

from importlib.metadata import entry_points

from sdk.plugins.base import TechnicalAssetPlugin

from app.core.logging import logger

ENTRY_POINT_GROUP = "data_product_portal.plugins"


def discover_plugins() -> list[type[TechnicalAssetPlugin]]:
    """Scan the entry point group and return every valid plugin class found.

    A plugin that fails to import, or doesn't subclass `TechnicalAssetPlugin`,
    is logged and skipped rather than crashing startup for every other
    plugin. A subclass missing a required attribute already failed at
    import time (see `TechnicalAssetPlugin.__init_subclass__`), so that
    case is caught here too.
    """
    plugins: list[type[TechnicalAssetPlugin]] = []
    for entry_point in entry_points(group=ENTRY_POINT_GROUP):
        try:
            plugin_cls = entry_point.load()
        except Exception:
            logger.exception(f"Failed to load plugin entry point '{entry_point.name}'")
            continue

        if not (
            isinstance(plugin_cls, type)
            and issubclass(plugin_cls, TechnicalAssetPlugin)
        ):
            logger.error(
                f"Plugin '{entry_point.name}' does not subclass TechnicalAssetPlugin - skipping"
            )
            continue

        plugins.append(plugin_cls)
    return plugins
