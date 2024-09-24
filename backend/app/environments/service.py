from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.environment_platform_configurations.model import (
    EnvironmentPlatformConfiguration as EnvironmentPlatformConfigurationModel,
)
from app.environment_platform_configurations.schema import (
    EnvironmentPlatformConfiguration,
)
from app.environment_platform_service_configurations.model import (
    EnvironmentPlatformServiceConfiguration as EnvPlatformServiceConfigurationModel,
)
from app.environment_platform_service_configurations.schema import (
    EnvironmentPlatformServiceConfiguration,
)
from app.environments.model import Environment as EnvironmentModel
from app.environments.schema import Environment


class EnvironmentService:
    def __init__(self, db: Session):
        self.db = db

    def get_environments(self) -> Sequence[Environment]:
        return self.db.scalars(select(EnvironmentModel)).all()

    def get_environment_platform_service_config(
        self, environment_id: UUID, platform_id: UUID, service_id: UUID
    ) -> EnvironmentPlatformServiceConfiguration:
        stmt = select(EnvPlatformServiceConfigurationModel).where(
            EnvPlatformServiceConfigurationModel.environment_id == environment_id,
            EnvPlatformServiceConfigurationModel.platform_id == platform_id,
            EnvPlatformServiceConfigurationModel.service_id == service_id,
        )
        return self.db.scalar(stmt)

    def get_environment_platform_config(
        self, environment_id: UUID, platform_id: UUID
    ) -> EnvironmentPlatformConfiguration:
        stmt = select(EnvironmentPlatformConfigurationModel).where(
            EnvironmentPlatformConfigurationModel.environment_id == environment_id,
            EnvironmentPlatformConfigurationModel.platform_id == platform_id,
        )
        return self.db.scalar(stmt)

    def get_environment_configs(
        self, environment_id: UUID
    ) -> Sequence[EnvironmentPlatformServiceConfiguration]:
        stmt = select(EnvPlatformServiceConfigurationModel).where(
            EnvPlatformServiceConfigurationModel.environment_id == environment_id
        )
        return self.db.scalars(stmt).all()
