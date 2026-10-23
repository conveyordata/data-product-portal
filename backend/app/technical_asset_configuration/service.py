from typing import TYPE_CHECKING, Optional, Sequence
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.data_products.model import ensure_data_product_exists
from app.database.deps import get_db_session
from app.technical_asset_configuration.schema_request import (
    RenderTechnicalAssetAccessPathRequest,
)

if TYPE_CHECKING:
    from app.users.schema import User

from app.plugins.platform import Platform
from app.plugins.registry import plugin_registry
from app.technical_asset_configuration.base_schema import (
    PluginContext,
    TechnicalAssetPlugin,
)
from app.technical_asset_configuration.schema_response import (
    PlatformTile,
    UIElementMetadataResponse,
)


class PluginService:
    def __init__(self, db: Session = Depends(get_db_session, scope="function")):
        self.db = db

    def get_all_technical_assets_ui_metadata(
        self,
    ) -> Sequence[UIElementMetadataResponse]:
        """Generate UI metadata for every enabled plugin"""
        return [
            self._build_metadata_response(plugin)
            for plugin in plugin_registry.enabled()
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
        self, plugin_class: type[TechnicalAssetPlugin]
    ) -> UIElementMetadataResponse:
        platform_meta = plugin_class.get_platform_metadata()
        return UIElementMetadataResponse(
            ui_metadata=plugin_class.get_ui_metadata(self.db),
            plugin=plugin_class.name,
            icon_data_uri=plugin_class.get_icon_data_uri(),
            platform=platform_meta.platform_key,
            display_name=platform_meta.display_name,
            icon_name=platform_meta.icon_name,
            result_label=platform_meta.result_label,
            result_tooltip=platform_meta.result_tooltip,
            detailed_name=platform_meta.detailed_name,
            shareable=platform_meta.shareable,
        )

    def get_platform_tiles(self) -> Sequence[PlatformTile]:
        """Build the complete platform tile structure for the UI"""
        enabled = plugin_registry.enabled()
        tiles = []
        for platform in plugin_registry.platforms():
            assets = [asset for asset in enabled if asset.platform is platform]
            if not assets and not plugin_registry.enabled_tool_types(platform):
                continue
            children = [self._asset_tile(asset) for asset in assets]
            if len(assets) == 1 and children[0].value == platform.key:
                tiles.append(children[0])
                continue
            tiles.append(
                PlatformTile(
                    label=platform.display_name,
                    value=platform.key,
                    icon_name=platform.icon_name,
                    icon_data_uri=platform.get_icon_data_uri(),
                    has_environments=platform.has_environments,
                    show_in_form=bool(assets),
                    children=children,
                )
            )
        return tiles

    def get_url(
        self,
        plugin_name: str,
        id: UUID,
        actor: "User",
        environment: Optional[str] = None,
    ) -> str:
        platform = self._platform_for_tile(plugin_name)
        try:
            return platform.get_url(id, self.db, actor, environment)
        except NotImplementedError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Plugin '{plugin_name}' does not implement URL retrieval",
            )

    def render_technical_asset_access_path(
        self, request: RenderTechnicalAssetAccessPathRequest
    ) -> str:
        template = request.configuration.get_platform_metadata().result_string_template

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found for the given technical asset type",
            )

        return request.configuration.render_template(
            template,
            plugin_context=PluginContext.build(
                ensure_data_product_exists(request.data_product_id, self.db),
                request.namespace,
                request.technical_mapping,
            ),
        )

    @staticmethod
    def _asset_tile(asset: type[TechnicalAssetPlugin]) -> PlatformTile:
        platform_meta = asset.get_platform_metadata()
        return PlatformTile(
            label=platform_meta.display_name,
            value=platform_meta.platform_key,
            icon_name=platform_meta.icon_name,
            icon_data_uri=asset.get_icon_data_uri(),
            has_environments=asset.platform.has_environments,
        )

    @staticmethod
    def _platform_for_tile(value: str) -> type[Platform]:
        platform = next(
            (
                platform
                for platform in plugin_registry.platforms()
                if platform.key == value
                or any(
                    asset.get_platform_metadata().platform_key == value
                    for asset in platform.asset_types
                )
            ),
            None,
        )
        if platform is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plugin '{value}' not found",
            )
        return platform
