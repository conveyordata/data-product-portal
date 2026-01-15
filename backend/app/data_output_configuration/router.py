from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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


# ADR-compliant endpoints
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
