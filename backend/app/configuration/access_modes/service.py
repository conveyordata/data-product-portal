from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import count

from app.abstract_data_product.input_ports.model import InputPortRequest
from app.configuration.access_modes.model import AccessMode
from app.configuration.access_modes.schema_request import (
    AccessModeCreate,
    AccessModeUpdate,
)
from app.data_products.technical_assets.model import TechnicalAsset
from app.database.deps import get_db_session
from app.technical_asset_configuration.base_model import TechnicalAssetConfiguration
from app.technical_asset_configuration.service import PluginService

ACCESS_MODE_NOT_FOUND_ERROR = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Access mode not found",
)
CAN_NOT_REMOVE_TECHNICAL_ASSET_TYPES_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Cannot remove the specified technical asset types because they are in use by technical assets or input port requests.",
)
CAN_NOT_REMOVE_ACCESS_MODE_IN_USE_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Cannot remove the specified access mode because it is in use by technical assets or input port requests.",
)


class AccessModeService:
    def __init__(
        self,
        db: Session = Depends(get_db_session),
        plugin_service: PluginService = Depends(PluginService),
    ) -> None:
        self.db = db
        self.plugin_service = plugin_service

    def create_access_mode(self, access_mode: AccessModeCreate) -> "AccessMode":
        plugins = self.plugin_service.get_all_technical_assets_ui_metadata()
        plugin_names = [plugin.plugin for plugin in plugins if plugin.show_in_form]
        for technical_asset_type in access_mode.technical_asset_types:
            if technical_asset_type not in plugin_names:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Technical asset type {technical_asset_type} does not exist or is not enabled",
                )
        access_mode_model = AccessMode(**access_mode.parse_pydantic_schema())
        self.db.add(access_mode_model)
        self.db.flush()
        return access_mode_model

    def update_access_mode(
        self, id: UUID, update: AccessModeUpdate
    ) -> type[AccessMode]:
        access_mode = self.db.get(AccessMode, id)
        if not access_mode:
            raise ACCESS_MODE_NOT_FOUND_ERROR
        asset_types_being_removed = [
            asset_type
            for asset_type in access_mode.technical_asset_types
            if asset_type not in update.technical_asset_types
        ]

        technical_asset_count = 0
        input_port_requests_count = 0
        if asset_types_being_removed:
            technical_asset_count = self.db.scalar(
                select(count(TechnicalAsset.id))
                .select_from(TechnicalAsset)
                .join(TechnicalAsset.configuration)
                .filter(
                    TechnicalAsset.access_modes.any(AccessMode.id == id),
                    TechnicalAssetConfiguration.configuration_type.in_(
                        asset_types_being_removed
                    ),
                )
            )
            input_port_requests_count = self.db.scalar(
                select(count(InputPortRequest.id))
                .select_from(InputPortRequest)
                .filter(
                    InputPortRequest.access_mode_id == id,
                )
            )

        if technical_asset_count > 0 or input_port_requests_count > 0:
            raise CAN_NOT_REMOVE_TECHNICAL_ASSET_TYPES_ERROR

        for key, value in update.parse_pydantic_schema().items():
            setattr(access_mode, key, value)
        self.db.flush()
        return access_mode

    def get_access_modes(self) -> list[type[AccessMode]]:
        return self.db.query(AccessMode).all()

    def delete_access_mode(self, id: UUID) -> None:
        access_mode = self.db.get(AccessMode, id)
        if not access_mode:
            raise ACCESS_MODE_NOT_FOUND_ERROR
        technical_asset_count = self.db.scalar(
            select(count(TechnicalAsset.id))
            .select_from(TechnicalAsset)
            .join(TechnicalAsset.configuration)
            .filter(
                TechnicalAsset.access_modes.any(AccessMode.id == id),
            )
        )
        input_port_requests_count = self.db.scalar(
            select(count(InputPortRequest.id))
            .select_from(InputPortRequest)
            .filter(
                InputPortRequest.access_mode_id == id,
            )
        )

        if technical_asset_count > 0 or input_port_requests_count > 0:
            raise CAN_NOT_REMOVE_ACCESS_MODE_IN_USE_ERROR

        self.db.delete(access_mode)
        self.db.flush()
