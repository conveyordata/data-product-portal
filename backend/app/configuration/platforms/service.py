from typing import Any, Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.configuration.environments.model import Environment as EnvironmentModel
from app.configuration.platforms.model import (
    PlatformEnvironmentSettings as PlatformEnvironmentSettingsModel,
)
from app.configuration.platforms.schema_response import (
    Platform,
    PlatformEnvironmentSettings,
    PlatformType,
    PlatformTypeKind,
)
from app.plugins.registry import plugin_registry


class PlatformSettingsService:
    def __init__(self, db: Session):
        self.db = db

    def get_platforms(self) -> Sequence[Platform]:
        return [
            Platform(
                key=platform.key,
                display_name=platform.display_name,
                icon_name=platform.icon_name,
                icon_data_uri=platform.get_icon_data_uri(),
                has_environments=platform.has_environments,
                settings_schema=platform.settings_model.model_json_schema(),
                types=[
                    PlatformType(
                        kind=PlatformTypeKind.Asset,
                        name=asset_type.name,
                        display_name=asset_type.get_platform_metadata().display_name,
                    )
                    for asset_type in plugin_registry.enabled()
                    if asset_type.platform is platform
                ]
                + [
                    PlatformType(kind=PlatformTypeKind.Tool, **tool_type.model_dump())
                    for tool_type in plugin_registry.enabled_tool_types(platform)
                ],
            )
            for platform in plugin_registry.platforms()
        ]

    def get_settings(
        self, platform_key: str, environment_id: UUID
    ) -> PlatformEnvironmentSettings:
        platform = plugin_registry.platform(platform_key)
        self._ensure_environment(environment_id)
        row = self.db.get(
            PlatformEnvironmentSettingsModel, (platform_key, environment_id)
        )
        return PlatformEnvironmentSettings(
            platform_key=platform_key,
            environment_id=environment_id,
            settings=row.settings
            if row
            else platform.settings_model().model_dump(mode="json"),
        )

    def update_settings(
        self, platform_key: str, environment_id: UUID, settings: dict[str, Any]
    ) -> PlatformEnvironmentSettings:
        platform = plugin_registry.platform(platform_key)
        self._ensure_environment(environment_id)
        try:
            validated = platform.settings_model.model_validate(settings)
        except ValidationError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
            )
        row = self.db.get(
            PlatformEnvironmentSettingsModel, (platform_key, environment_id)
        ) or PlatformEnvironmentSettingsModel(
            platform_key=platform_key, environment_id=environment_id
        )
        row.settings = validated.model_dump(mode="json")
        self.db.add(row)
        self.db.flush()
        return PlatformEnvironmentSettings.model_validate(row)

    def get_for_environment_name(
        self, platform_key: str, environment_name: Optional[str]
    ) -> dict[str, Any]:
        row = self.db.scalar(
            select(PlatformEnvironmentSettingsModel)
            .join(PlatformEnvironmentSettingsModel.environment)
            .where(
                PlatformEnvironmentSettingsModel.platform_key == platform_key,
                EnvironmentModel.name == environment_name,
            )
        )
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Missing {platform_key} settings for environment {environment_name}",
            )
        return row.settings

    def get_all(self) -> Sequence[PlatformEnvironmentSettingsModel]:
        return self.db.scalars(select(PlatformEnvironmentSettingsModel)).all()

    def _ensure_environment(self, environment_id: UUID) -> None:
        if not self.db.scalar(select(EnvironmentModel).filter_by(id=environment_id)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Environment {environment_id} does not exist",
            )
