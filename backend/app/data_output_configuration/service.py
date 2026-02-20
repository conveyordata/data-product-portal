from typing import TYPE_CHECKING, Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.configuration.platforms.platform_services.model import PlatformService
from app.data_output_configuration.schema_request import (
    RenderTechnicalAssetAccessPathRequest,
)

if TYPE_CHECKING:
    from app.users.schema import User

from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
)
from app.data_output_configuration.schema_response import (
    PlatformTile,
    UIElementMetadataResponse,
)
from app.platform_service_configurations.schema import PlatformServiceConfiguration
from app.settings import settings


class PluginService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_technical_assets_ui_metadata(
        self,
    ) -> Sequence[UIElementMetadataResponse]:
        """Generate UI metadata for all registered data output types"""
        data_output_configurations = AssetProviderPlugin.__subclasses__()
        configured_plugins = settings.ENABLED_PLUGINS
        configured_metadata = [
            name
            for name in data_output_configurations
            if name.__name__ in configured_plugins
        ]
        return [
            metadata_response
            for plugin in configured_metadata
            if (metadata_response := self._build_metadata_response(plugin)) is not None
        ]

    def get_technical_asset_ui_metadata_by_name(
        self, plugin_name: str
    ) -> UIElementMetadataResponse:
        all_plugins = self.get_all_technical_assets_ui_metadata()

        # Find the plugin by name
        plugin = next((p for p in all_plugins if p.plugin == plugin_name), None)
        if plugin is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plugin '{plugin_name}' not found",
            )

        return plugin

    def _build_metadata_response(
        self, plugin_class: type[AssetProviderPlugin]
    ) -> Optional[UIElementMetadataResponse]:
        """Build a complete metadata response for a plugin"""
        try:
            platform_meta = plugin_class.get_platform_metadata()
            return UIElementMetadataResponse(
                ui_metadata=plugin_class.get_ui_metadata(self.db),
                plugin=plugin_class.__name__,
                platform=platform_meta.platform_key,
                display_name=platform_meta.display_name,
                icon_name=platform_meta.icon_name,
                parent_platform=platform_meta.parent_platform,
                result_label=platform_meta.result_label,
                has_environments=platform_meta.has_environments,
                result_tooltip=platform_meta.result_tooltip,
                detailed_name=platform_meta.detailed_name,
                show_in_form=platform_meta.show_in_form,
            )
        except NotImplementedError:
            return UIElementMetadataResponse(
                not_configured=True,
                ui_metadata=[],
                plugin=plugin_class.__name__,
                platform=platform_meta.platform_key,
                display_name=platform_meta.display_name,
                icon_name=platform_meta.icon_name,
                parent_platform=platform_meta.parent_platform,
                show_in_form=platform_meta.show_in_form,
                result_label=platform_meta.result_label,
                result_tooltip=platform_meta.result_tooltip,
                detailed_name=platform_meta.detailed_name,
                has_environments=platform_meta.has_environments,
            )

    def get_platform_tiles(
        self, configs: Sequence[PlatformServiceConfiguration]
    ) -> Sequence[PlatformTile]:
        """Build the complete platform tile structure for the UI"""
        all_metadata = self.get_all_technical_assets_ui_metadata()
        # Filter to only configured platforms
        return self._build_tile_hierarchy(all_metadata)

    def get_url(
        self,
        plugin_name: str,
        id: UUID,
        db: Session,
        actor: "User",
        environment: Optional[str] = None,
    ) -> str:
        data_output_configurations = AssetProviderPlugin.__subclasses__()
        plugin_class = next(
            (
                cls
                for cls in data_output_configurations
                if cls.get_platform_metadata().platform_key == plugin_name
            ),
            None,
        )
        # If no direct match, check if it's a parent platform
        if not plugin_class:
            plugin_class = next(
                (
                    cls
                    for cls in data_output_configurations
                    if cls.get_platform_metadata().parent_platform == plugin_name
                ),
                None,
            )
        if not plugin_class:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plugin '{plugin_name}' not found",
            )
        try:
            return plugin_class.get_url(id, db, actor, environment)
        except NotImplementedError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Plugin '{plugin_name}' does not implement URL retrieval",
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
                has_environments=meta.has_environments,
                has_config=True,
                show_in_form=meta.show_in_form,
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
                        has_environments=True,
                        has_config=True,
                        show_in_form=meta.show_in_form,
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

    def render_technical_asset_access_path(
        self, request: RenderTechnicalAssetAccessPathRequest
    ) -> str:
        template = self.db.scalar(
            select(PlatformService.result_string_template).where(
                PlatformService.id == request.service_id,
                PlatformService.platform_id == request.platform_id,
            )
        )

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found for the given platform and service",
            )

        return request.configuration.render_template(template)
