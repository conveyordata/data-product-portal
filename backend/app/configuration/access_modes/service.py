from typing import Annotated, Sequence
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import any_, delete, exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.configuration.access_modes.model import AccessMode, DefaultAccessMode
from app.configuration.access_modes.schema_request import (
    AccessModeCreate,
    AccessModeUpdate,
)
from app.configuration.access_modes.schema_response import AccessModeWithType
from app.data_products.technical_assets.model import (
    TechnicalAsset,
    TechnicalAssetAccessMode,
)
from app.database.database import UNFILTERED
from app.database.deps import DbSession
from app.technical_asset_configuration.base_model import TechnicalAssetConfiguration
from app.technical_asset_configuration.service import PluginService

ACCESS_MODE_NOT_FOUND_ERROR = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Access mode not found",
)
CAN_NOT_REMOVE_TECHNICAL_ASSET_TYPES_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Cannot remove the specified technical asset types because they are in use by technical assets.",
)
CAN_NOT_REMOVE_ACCESS_MODE_IN_USE_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Cannot remove the specified access mode because it is in use by technical assets or input port requests.",
)
CAN_NOT_REMOVE_DEFAULT_ACCESS_MODE_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Cannot remove the default access mode of a technical asset type that has other access modes. Make another access mode the default first.",
)
INVALID_DEFAULT_TECHNICAL_ASSET_TYPES_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="An access mode can only be the default for technical asset types it applies to.",
)


class AccessModeService:
    def __init__(
        self,
        db: DbSession,
        plugin_service: Annotated[PluginService, Depends(PluginService)],
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
        self._ensure_valid_default_types(access_mode)
        access_mode_schema = access_mode.parse_pydantic_schema()
        default_for = access_mode_schema.pop("default_for_technical_asset_types")
        access_mode_model = AccessMode(**access_mode_schema)
        self.db.add(access_mode_model)
        self.db.flush()
        self._assign_defaults(access_mode_model, default_for)
        return access_mode_model

    def update_access_mode(
        self, id: UUID, update: AccessModeUpdate
    ) -> type[AccessMode]:
        access_mode = self.db.get(AccessMode, id)
        if not access_mode:
            raise ACCESS_MODE_NOT_FOUND_ERROR
        self._ensure_valid_default_types(update)
        asset_types_being_removed = [
            asset_type
            for asset_type in access_mode.technical_asset_types
            if asset_type not in update.technical_asset_types
        ]

        in_use = self._in_use_technical_asset_types([access_mode])[access_mode.id]
        if in_use.intersection(asset_types_being_removed):
            raise CAN_NOT_REMOVE_TECHNICAL_ASSET_TYPES_ERROR
        self._ensure_types_keep_a_default(access_mode, asset_types_being_removed)
        # Just checked: no other access mode covers the types this one is the default
        # for, so we are allowed to delete these defaults.
        self.db.execute(
            delete(DefaultAccessMode).where(
                DefaultAccessMode.access_mode_id == access_mode.id,
                DefaultAccessMode.technical_asset_type.in_(asset_types_being_removed),
            )
        )

        update_schema = update.parse_pydantic_schema()
        default_for = update_schema.pop("default_for_technical_asset_types")
        for key, value in update_schema.items():
            setattr(access_mode, key, value)
        self.db.flush()
        self._assign_defaults(access_mode, default_for)
        return access_mode

    def get_access_modes(self) -> list[AccessModeWithType]:
        access_modes = self.db.scalars(
            select(AccessMode).options(selectinload(AccessMode.defaults))
        ).all()
        in_use = self._in_use_technical_asset_types(access_modes)
        return [
            AccessModeWithType(
                id=access_mode.id,
                name=access_mode.name,
                description=access_mode.description,
                technical_asset_types=access_mode.technical_asset_types,
                default_for_technical_asset_types=access_mode.default_for_technical_asset_types,
                in_use_technical_asset_types=sorted(in_use[access_mode.id]),
            )
            for access_mode in access_modes
        ]

    def delete_access_mode(self, id: UUID) -> None:
        access_mode = self.db.get(AccessMode, id)
        if not access_mode:
            raise ACCESS_MODE_NOT_FOUND_ERROR
        self._ensure_types_keep_a_default(
            access_mode, access_mode.technical_asset_types
        )
        # Technical assets and input port requests reference access modes through
        # foreign keys, so the database refuses to delete an access mode in use.
        try:
            with self.db.begin_nested():
                self.db.delete(access_mode)
        except IntegrityError as error:
            raise CAN_NOT_REMOVE_ACCESS_MODE_IN_USE_ERROR from error

    def _in_use_technical_asset_types(
        self, access_modes: Sequence[AccessMode]
    ) -> dict[UUID, set[str]]:
        """Per access mode, the technical asset types it can't drop because technical assets of that type use it."""
        access_mode_ids = [access_mode.id for access_mode in access_modes]
        used_by_technical_assets = self.db.execute(
            select(
                TechnicalAssetAccessMode.access_mode_id,
                TechnicalAssetConfiguration.configuration_type,
            )
            .join(
                TechnicalAsset,
                TechnicalAsset.id == TechnicalAssetAccessMode.technical_asset_id,
            )
            .join(TechnicalAsset.configuration)
            .where(TechnicalAssetAccessMode.access_mode_id.in_(access_mode_ids))
            .distinct(),
            execution_options=UNFILTERED,
        ).all()
        in_use: dict[UUID, set[str]] = {
            access_mode.id: set() for access_mode in access_modes
        }
        for access_mode_id, technical_asset_type in used_by_technical_assets:
            in_use[access_mode_id].add(technical_asset_type)
        return in_use

    @staticmethod
    def _ensure_valid_default_types(
        access_mode: AccessModeCreate | AccessModeUpdate,
    ) -> None:
        if not set(access_mode.default_for_technical_asset_types).issubset(
            access_mode.technical_asset_types
        ):
            raise INVALID_DEFAULT_TECHNICAL_ASSET_TYPES_ERROR

    def _assign_defaults(self, access_mode: AccessMode, default_for: list[str]) -> None:
        """Makes this access mode the default for types without one and for `default_for`."""
        current_defaults = {
            default.technical_asset_type: default
            for default in self.db.scalars(
                select(DefaultAccessMode).where(
                    DefaultAccessMode.technical_asset_type.in_(
                        access_mode.technical_asset_types
                    )
                )
            )
        }
        for technical_asset_type in access_mode.technical_asset_types:
            current_default = current_defaults.get(technical_asset_type)
            if current_default is None:
                self.db.add(
                    DefaultAccessMode(
                        technical_asset_type=technical_asset_type,
                        access_mode_id=access_mode.id,
                    )
                )
            elif technical_asset_type in default_for:
                current_default.access_mode_id = access_mode.id
        self.db.flush()

    def _ensure_types_keep_a_default(
        self, access_mode: AccessMode, technical_asset_types: list[str]
    ) -> None:
        """Blocks dropping types this access mode is the default for while other access modes still cover them.
        The user should first switch the default.
        """
        defaulted_types = self.db.scalars(
            select(DefaultAccessMode.technical_asset_type).where(
                DefaultAccessMode.access_mode_id == access_mode.id,
                DefaultAccessMode.technical_asset_type.in_(technical_asset_types),
            )
        ).all()
        for technical_asset_type in defaulted_types:
            if self.db.scalar(
                select(
                    exists().where(
                        AccessMode.id != access_mode.id,
                        technical_asset_type == any_(AccessMode.technical_asset_types),
                    )
                )
            ):
                raise CAN_NOT_REMOVE_DEFAULT_ACCESS_MODE_ERROR
