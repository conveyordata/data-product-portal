from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.environment_platform_configurations.model import (
    EnvironmentPlatformConfiguration as EnvironmentPlatformConfigurationModel,
)
from app.environment_platform_configurations.schema import (
    EnvironmentPlatformConfiguration,
)


class EnvironmentPlatformConfigurationService:
    def __init__(self, db: Session):
        self.db = db

    def get_environment_platform_config(
        self, environment_id: UUID, platform_id: UUID
    ) -> EnvironmentPlatformConfiguration:
        stmt = select(EnvironmentPlatformConfigurationModel).where(
            EnvironmentPlatformConfigurationModel.environment_id == environment_id,
            EnvironmentPlatformConfigurationModel.platform_id == platform_id,
        )
        return self.db.scalar(stmt)
