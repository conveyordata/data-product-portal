from importlib.metadata import entry_points
from typing import Annotated, Optional

from fastapi import HTTPException, status
from pydantic import AfterValidator

from app.core.logging import logger
from app.settings import settings
from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin

ENTRY_POINT_GROUP = "data_product_portal.plugins"


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: Optional[dict[str, type[TechnicalAssetPlugin]]] = None

    def _discover(self) -> dict[str, type[TechnicalAssetPlugin]]:
        plugins: dict[str, type[TechnicalAssetPlugin]] = {}

        for entry_point in entry_points(group=ENTRY_POINT_GROUP):
            plugin = entry_point.load()
            if not (
                isinstance(plugin, type) and issubclass(plugin, TechnicalAssetPlugin)
            ):
                raise Exception(
                    "The registered plugin does not subclass TechnicalAssetPlugin or is not a class"
                )
            plugins[plugin.name] = plugin

        logger.info(f"Discovered plugins: {', '.join(sorted(plugins)) or 'none'}")
        return plugins

    def discovered(self) -> list[type[TechnicalAssetPlugin]]:
        if self._plugins is None:
            self._plugins = self._discover()
        return list(self._plugins.values())

    def enabled(
        self,
    ) -> list[type[TechnicalAssetPlugin]]:
        return [
            plugin
            for plugin in self.discovered()
            if plugin.name in settings.ENABLED_PLUGINS
        ]

    def get(self, name: str) -> type[TechnicalAssetPlugin]:
        plugin = next((p for p in self.discovered() if p.name == name), None)
        if plugin is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Plugin '{name}' is not installed",
            )
        return plugin


plugin_registry = PluginRegistry()


def ensure_technical_asset_type(name: str) -> str:
    plugin = next((p for p in plugin_registry.discovered() if p.name == name), None)
    if plugin is None or not hasattr(plugin, "Meta"):
        raise ValueError(f"'{name}' is not an installed Technical Asset Type")
    return name


TechnicalAssetType = Annotated[str, AfterValidator(ensure_technical_asset_type)]
