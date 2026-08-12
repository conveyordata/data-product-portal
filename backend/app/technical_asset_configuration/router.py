from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic.json_schema import SkipJsonSchema

from app.core.auth.auth import get_authenticated_user
from app.core.authz.authorization import Authorization
from app.core.authz.authorization import AuthorizationAction as Action
from app.core.authz.resolvers import DataProductResolver
from app.technical_asset_configuration.schema_request import (
    RenderTechnicalAssetAccessPathRequest,
)
from app.technical_asset_configuration.schema_response import (
    PlatformTileResponse,
    PluginResponse,
    RenderTechnicalAssetAccessPathResponse,
    UIElementMetadataResponse,
    URLResponse,
)
from app.technical_asset_configuration.service import PluginService
from app.users.schema import User

router = APIRouter(
    prefix="/v2/plugins",
    tags=["Plugins"],
)


@router.get("/platform-tiles")
def get_platform_tiles(
    plugin_service: PluginService = Depends(PluginService),
) -> PlatformTileResponse:
    return PlatformTileResponse(platform_tiles=plugin_service.get_platform_tiles())


@router.get("/")
def get_plugins(
    plugin_service: PluginService = Depends(PluginService),
) -> PluginResponse:
    """List all available plugins with their metadata (ADR-compliant endpoint)"""
    return PluginResponse(plugins=plugin_service.get_all_technical_assets_ui_metadata())


@router.get("/{plugin_name}/form")
def get_plugin_form(
    plugin_name: str,
    plugin_service: PluginService = Depends(PluginService),
) -> UIElementMetadataResponse:
    """Get form metadata for a specific plugin (ADR-compliant endpoint)"""
    return plugin_service.get_technical_asset_ui_metadata_by_name(plugin_name)


@router.get(
    "/{plugin_name}/url",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__READ_INTEGRATIONS, DataProductResolver
            )
        ),
    ],
)
def get_plugin_url(
    plugin_name: str,
    id: UUID,
    environment: Annotated[str | SkipJsonSchema[None], Query()] = None,
    plugin_service: PluginService = Depends(PluginService),
    actor: User = Depends(get_authenticated_user),
) -> URLResponse:
    """Get the URL for the access tile of a specific plugin"""
    return URLResponse(url=plugin_service.get_url(plugin_name, id, actor, environment))


@router.post("/render_technical_asset_access_path")
def render_technical_asset_access_path(
    request: RenderTechnicalAssetAccessPathRequest,
    plugin_service: PluginService = Depends(PluginService),
) -> RenderTechnicalAssetAccessPathResponse:
    return RenderTechnicalAssetAccessPathResponse(
        technical_asset_access_path=plugin_service.render_technical_asset_access_path(
            request
        )
    )
