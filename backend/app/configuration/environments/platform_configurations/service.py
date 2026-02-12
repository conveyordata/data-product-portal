from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.configuration.environments.model import Environment as EnvironmentModel
from app.configuration.environments.platform_configurations.model import (
    EnvironmentPlatformConfiguration as EnvironmentPlatformConfigurationModel,
)
from app.configuration.environments.platform_configurations.schema_response import (
    EnvironmentPlatformConfigGet,
)
from app.configuration.platforms.model import Platform as PlatformModel


class EnvironmentPlatformConfigurationService:
    def __init__(self, db: Session):
        self.db = db

    def get_environment_platform_config(
        self, environment_id: UUID, platform_id: UUID
    ) -> EnvironmentPlatformConfigGet:
        stmt = select(EnvironmentPlatformConfigurationModel).where(
            EnvironmentPlatformConfigurationModel.environment_id == environment_id,
            EnvironmentPlatformConfigurationModel.platform_id == platform_id,
        )
        return self.db.scalar(stmt)

    def get_env_platform_config(self, environment: str, platform_name: str) -> str:
        environment_model = self.db.scalar(
            select(EnvironmentModel).where(EnvironmentModel.name == environment)
        )
        platform = self.db.scalar(
            select(PlatformModel).where(PlatformModel.name == platform_name)
        )

        stmt = select(EnvironmentPlatformConfigurationModel).where(
            EnvironmentPlatformConfigurationModel.environment_id
            == environment_model.id,
            EnvironmentPlatformConfigurationModel.platform_id == platform.id,
        )
        config = self.db.scalar(stmt)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Missing Platform Environment configuration for {platform_name}"
                ),
            )
        return config.config
