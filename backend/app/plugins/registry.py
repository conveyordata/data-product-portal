from importlib.metadata import entry_points
from typing import Optional

from fastapi import HTTPException, status

from app.core.logging import logger
from app.plugins.platform import Platform, ToolType
from app.settings import settings
from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin

ENTRY_POINT_GROUP = "data_product_portal.platforms"


class PluginRegistry:
    def __init__(self) -> None:
        self._platforms: Optional[dict[str, type[Platform]]] = None

    def _discover(self) -> dict[str, type[Platform]]:
        platforms: dict[str, type[Platform]] = {}

        for entry_point in entry_points(group=ENTRY_POINT_GROUP):
            platform = entry_point.load()
            if not (isinstance(platform, type) and issubclass(platform, Platform)):
                raise Exception(
                    "The registered platform does not subclass Platform or is not a class"
                )
            for asset_type in platform.asset_types:
                asset_type.platform = platform
            platforms[platform.key] = platform

        logger.info(f"Discovered platforms: {', '.join(sorted(platforms)) or 'none'}")
        return platforms

    def platforms(self) -> list[type[Platform]]:
        if self._platforms is None:
            self._platforms = self._discover()
        return list(self._platforms.values())

    def platform(self, key: str) -> type[Platform]:
        platform = next((p for p in self.platforms() if p.key == key), None)
        if platform is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform '{key}' is not installed",
            )
        return platform

    def discovered(self) -> list[type[TechnicalAssetPlugin]]:
        return [
            asset_type
            for platform in self.platforms()
            for asset_type in platform.asset_types
        ]

    def enabled(
        self,
    ) -> list[type[TechnicalAssetPlugin]]:
        return [
            plugin
            for plugin in self.discovered()
            if plugin.name in settings.ENABLED_PLUGINS
        ]

    def enabled_tool_types(self, platform: type[Platform]) -> list[ToolType]:
        return [
            tool_type
            for tool_type in platform.tool_types
            if tool_type.name in settings.ENABLED_PLUGINS
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
