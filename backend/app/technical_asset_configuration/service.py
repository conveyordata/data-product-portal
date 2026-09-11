from typing import TYPE_CHECKING, Any, Optional, Sequence
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sdk.plugins.base import TechnicalAssetPlugin
from sdk.plugins.context import PluginContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.configuration.environments.model import Environment as EnvironmentModel
from app.configuration.platforms.platform_services.model import PlatformService
from app.core.logging import logger
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.technical_assets.model import TechnicalAsset
from app.database.deps import get_db_session
from app.plugins.loader import discover_plugins
from app.plugins.runtime import call_plugin
from app.technical_asset_configuration.schema_request import (
    RenderTechnicalAssetAccessPathRequest,
)

if TYPE_CHECKING:
    from app.users.schema import User

from app.settings import settings
from app.technical_asset_configuration.base_schema import (
    AssetProviderPlugin,
    UIElementMetadata,
    UIElementString,
)
from app.technical_asset_configuration.enums import UIElementType
from app.technical_asset_configuration.schema_response import (
    PlatformTile,
    UIElementMetadataResponse,
)


class PluginService:
    def __init__(self, db: Session = Depends(get_db_session)):
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
            if name.name in configured_plugins
        ]
        built_in = [
            metadata_response
            for plugin in configured_metadata
            if (metadata_response := self._build_metadata_response(plugin)) is not None
        ]
        dynamic = [
            self._build_dynamic_plugin_metadata_response(plugin_cls)
            for plugin_cls in discover_plugins()
        ]
        return built_in + dynamic

    def _build_dynamic_plugin_metadata_response(
        self, plugin_cls: type[TechnicalAssetPlugin]
    ) -> UIElementMetadataResponse:
        """Adapt a dynamically loaded plugin's minimal field vocabulary
        (ADR-0024) into the same UI metadata shape the existing,
        metadata-driven create-technical-asset form already renders.

        Only "string" fields are supported for now - see the ADR, "The
        plugin's field vocabulary, and who owns turning it into a form".
        """
        ui_metadata = []
        for field in plugin_cls.fields:
            field_type = field.get("type", "string")
            if field_type != "string":
                logger.warning(
                    f"Plugin '{plugin_cls.key}' field '{field.get('name')}' has "
                    f"unsupported type '{field_type}' - skipping. Only 'string' "
                    "fields are rendered by the portal today."
                )
                continue
            ui_metadata.append(
                UIElementMetadata(
                    name=field["name"],
                    label=field.get("label", field["name"]),
                    type=UIElementType.String,
                    required=field.get("required", False),
                    tooltip=field.get("tooltip"),
                    string=UIElementString(pattern=field.get("pattern")),
                )
            )
        return UIElementMetadataResponse(
            ui_metadata=ui_metadata,
            plugin=plugin_cls.key,
            platform=plugin_cls.key,
            display_name=plugin_cls.display_name,
            # Not a bundled frontend asset - fetched from the portal at
            # render time. See icon-loader.ts's "dynamic:" prefix handling.
            icon_name=f"dynamic:{plugin_cls.key}",
            has_environments=plugin_cls.has_environments,
            result_label="Resulting value",
            result_tooltip="The value you can access through this technical asset",
            detailed_name=plugin_cls.display_name,
            show_in_form=True,
            is_dynamic_plugin=True,
        )

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

    def get_platform_tiles(self) -> Sequence[PlatformTile]:
        """Build the complete platform tile structure for the UI"""
        all_metadata = self.get_all_technical_assets_ui_metadata()
        # Filter to only configured platforms
        return self._build_tile_hierarchy(all_metadata)

    def get_url(
        self,
        plugin_name: str,
        id: UUID,
        actor: "User",
        environment: Optional[str] = None,
    ) -> str:
        dynamic_plugin_cls = next(
            (p for p in discover_plugins() if p.key == plugin_name), None
        )
        if dynamic_plugin_cls:
            return self._get_dynamic_plugin_url(
                dynamic_plugin_cls, id, actor, environment
            )

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
            return plugin_class.get_url(id, self.db, actor, environment)
        except NotImplementedError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Plugin '{plugin_name}' does not implement URL retrieval",
            )

    def _get_dynamic_plugin_url(
        self,
        plugin_cls: type[TechnicalAssetPlugin],
        id: UUID,
        actor: "User",
        environment: Optional[str] = None,
    ) -> str:
        # `id` is a technical asset id when called from a technical asset's
        # own card, but the data-product-level "access data" grid
        # (DataProductActions.tsx) calls this same endpoint with the data
        # product's own id instead - built-in types tolerate this today by
        # mostly ignoring `id` (e.g. Azure Blob's own get_url() always
        # returns a static URL). Match that: degrade to empty values/context
        # rather than 404 when `id` doesn't resolve to a technical asset.
        technical_asset = self.db.get(TechnicalAsset, id)
        values: dict[str, Any] = {}
        if technical_asset:
            plugin_row = self.db.get(plugin_cls.model, id)
            if plugin_row:
                values = {
                    column.name: getattr(plugin_row, column.name)
                    for column in plugin_row.__table__.columns
                    if column.name != "id"
                }
            data_product_id = technical_asset.owner_id
            context = PluginContext(
                technical_asset_id=id,
                technical_asset_name=technical_asset.name,
                data_product_id=data_product_id,
                actor=actor,
            )
        else:
            data_product_id = id
            context = PluginContext(data_product_id=id, actor=actor)

        if plugin_cls.has_environments:
            if not environment:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Environment is required to get the URL for the '{plugin_cls.key}' plugin",
                )
            # Reuses the portal's own `Environment` table and the same
            # `{{}}` -> namespace substitution built-in types already do
            # (see `app.core.aws.get_url._get_data_product_role_arn`) -
            # deliberate, per ADR-0024's own decision driver to build on
            # top of the existing platform/environment data model rather
            # than invent a plugin-specific one.
            env = self.db.scalar(
                select(EnvironmentModel).where(EnvironmentModel.name == environment)
            )
            if not env:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Environment '{environment}' not found",
                )
            data_product = self.db.get(DataProductModel, data_product_id)
            namespace = data_product.namespace if data_product else None
            context.environment = environment
            context.environment_context = (
                env.context.replace("{{}}", namespace)
                if env.context and namespace
                else env.context
            )
            context.namespace = namespace

        result = call_plugin(
            plugin_cls.key, "get_url", plugin_cls.get_url, values, context
        )
        if not result.ok:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=result.error
            )
        return result.value

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
        if request.plugin_key:
            return self._render_dynamic_plugin_access_path(
                request.plugin_key, request.values or {}
            )

        if request.configuration is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="configuration is required",
            )
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

    def _render_dynamic_plugin_access_path(
        self, plugin_key: str, values: dict[str, Any]
    ) -> str:
        plugin_cls = next((p for p in discover_plugins() if p.key == plugin_key), None)
        if not plugin_cls:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No plugin registered for key '{plugin_key}'",
            )
        result = call_plugin(
            plugin_cls.key,
            "render_result",
            plugin_cls.render_result,
            values,
            PluginContext(),
        )
        if not result.ok:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=result.error
            )
        return result.value
