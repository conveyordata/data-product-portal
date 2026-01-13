from typing import Sequence

from sqlalchemy.orm import Session

from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
)
from app.data_output_configuration.schema_response import (
    PlatformTile,
    UIElementMetadataResponse,
)


class PluginService:
    def __init__(self, db: Session):
        self.db = db

    def get_technical_asset_ui_metadata(
        self,
    ) -> Sequence[UIElementMetadataResponse]:
        """Generate UI metadata for all registered data output types"""
        data_output_configurations = AssetProviderPlugin.__subclasses__()

        return [
            self._build_metadata_response(plugin)
            for plugin in data_output_configurations
        ]

    def _build_metadata_response(
        self, plugin_class: type[AssetProviderPlugin]
    ) -> UIElementMetadataResponse:
        """Build a complete metadata response for a plugin"""
        platform_meta = plugin_class.get_platform_metadata()
        return UIElementMetadataResponse(
            ui_metadata=plugin_class.get_ui_metadata(),
            plugin=plugin_class.__name__,
            platform=platform_meta.platform_key,
            display_name=platform_meta.display_name,
            icon_name=platform_meta.icon_name,
            parent_platform=platform_meta.parent_platform,
            result_label=platform_meta.result_label,
            result_tooltip=platform_meta.result_tooltip,
        )

    def get_platform_tiles(self, configs: Sequence) -> Sequence[PlatformTile]:
        """Build the complete platform tile structure for the UI"""
        all_metadata = self.get_technical_asset_ui_metadata()

        # Filter to only configured platforms
        configured_metadata = [
            meta for meta in all_metadata if self._has_config(meta, configs)
        ]

        # Build tile hierarchy
        return self._build_tile_hierarchy(configured_metadata)

    def _has_config(self, meta: UIElementMetadataResponse, configs: Sequence) -> bool:
        """Check if a platform has configuration"""
        return any(
            config.service.name.lower() == meta.display_name.lower()
            for config in configs
        )

    def _build_tile_hierarchy(
        self, metadata_list: Sequence[UIElementMetadataResponse]
    ) -> list[PlatformTile]:
        """Organize tiles into parent-child hierarchy"""
        parent_tiles: dict[str, PlatformTile] = {}
        child_tiles: dict[str, list[PlatformTile]] = {}

        for meta in metadata_list:
            tile = PlatformTile(
                label=meta.display_name,
                value=meta.platform,
                icon_name=meta.icon_name,
                has_menu=True,
                has_config=True,
                children=[],
            )

            if meta.parent_platform:
                # Add as child
                child_tiles.setdefault(meta.parent_platform, []).append(tile)

                # Ensure parent exists
                if meta.parent_platform not in parent_tiles:
                    parent_tiles[meta.parent_platform] = PlatformTile(
                        label=meta.parent_platform.upper(),
                        value=meta.parent_platform,
                        icon_name=f"{meta.parent_platform}-logo.svg",
                        has_menu=True,
                        has_config=True,
                        children=[],
                    )
            else:
                # Add as top-level tile
                parent_tiles.setdefault(meta.platform, tile)

        # Attach children to parents
        for parent_key, children in child_tiles.items():
            if parent_key in parent_tiles:
                parent_tiles[parent_key].children = children

        return list(parent_tiles.values())
