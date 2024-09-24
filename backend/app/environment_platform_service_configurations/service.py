from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.environment_platform_service_configurations.model import (
    EnvironmentPlatformServiceConfiguration as EnvPlatformServiceConfigurationModel,
)
from app.environment_platform_service_configurations.schema import (
    EnvironmentPlatformServiceConfiguration,
)


class EnvironmentPlatformServiceConfigurationService:
    def __init__(self, db: Session):
        self.db = db

    def get_environment_platform_service_config(
        self, environment_id: UUID, platform_id: UUID, service_id: UUID
    ) -> EnvironmentPlatformServiceConfiguration:
        stmt = select(EnvPlatformServiceConfigurationModel).where(
            EnvPlatformServiceConfigurationModel.environment_id == environment_id,
            EnvPlatformServiceConfigurationModel.platform_id == platform_id,
            EnvPlatformServiceConfigurationModel.service_id == service_id,
        )
        return self.db.scalar(stmt)

    def get_all_platform_service_configs(
        self, platform_id: UUID, service_id: UUID
    ) -> Sequence[EnvironmentPlatformServiceConfiguration]:
        stmt = select(EnvPlatformServiceConfigurationModel).where(
            EnvPlatformServiceConfigurationModel.platform_id == platform_id,
            EnvPlatformServiceConfigurationModel.service_id == service_id,
        )
        return self.db.scalars(stmt).all()

    def get_environment_platform_service_configs(
        self, environment_id: UUID
    ) -> Sequence[EnvironmentPlatformServiceConfiguration]:
        stmt = select(EnvPlatformServiceConfigurationModel).where(
            EnvPlatformServiceConfigurationModel.environment_id == environment_id
        )
        return self.db.scalars(stmt).all()

    def get_environment_platform_service_config_by_id(
        self, config_id: UUID
    ) -> EnvironmentPlatformServiceConfiguration:
        stmt = select(EnvPlatformServiceConfigurationModel).where(
            EnvPlatformServiceConfigurationModel.id == config_id
        )
        return self.db.scalar(stmt)
