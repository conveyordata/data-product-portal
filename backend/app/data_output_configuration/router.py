from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz.authorization import Authorization
from app.core.authz.authorization import AuthorizationAction as Action
from app.core.authz.resolvers import DataProductResolver
from app.data_output_configuration.schema_response import (
    PlatformTileResponse,
    PluginResponse,
    UIElementMetadataResponse,
)
from app.data_output_configuration.service import PluginService
from app.database.database import get_db_session
from app.platform_service_configurations.service import (
    PlatformServiceConfigurationService,
)
from app.users.schema import User

router = APIRouter(
    prefix="/v2/plugins",
    tags=["Plugins"],
)


@router.get("/platform-tiles")
def get_platform_tiles(
    db: Session = Depends(get_db_session),
) -> PlatformTileResponse:
    configs = PlatformServiceConfigurationService(
        db
    ).get_all_platform_service_configurations()
    return PlatformTileResponse(
        platform_tiles=PluginService(db).get_platform_tiles(configs)
    )


@router.get("/")
def get_plugins(
    db: Session = Depends(get_db_session),
) -> PluginResponse:
    """List all available plugins with their metadata (ADR-compliant endpoint)"""
    return PluginResponse(
        plugins=PluginService(db).get_all_technical_assets_ui_metadata()
    )


@router.get("/{plugin_name}/form")
def get_plugin_form(
    plugin_name: str,
    db: Session = Depends(get_db_session),
) -> UIElementMetadataResponse:
    """Get form metadata for a specific plugin (ADR-compliant endpoint)"""
    return PluginService(db).get_technical_asset_ui_metadata_by_name(plugin_name)


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
    environment: Optional[str] = None,
    db: Session = Depends(get_db_session),
    actor: User = Depends(get_authenticated_user),
) -> str:
    """Get the URL for the access tile of a specific plugin"""
    return PluginService(db).get_url(plugin_name, id, db, actor, environment)
