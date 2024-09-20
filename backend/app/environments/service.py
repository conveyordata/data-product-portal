from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.environments.model import (
    Environment,
    EnvPlatformConfig,
    EnvPlatformServiceConfig,
)


class EnvironmentService:
    def __init__(self, db: Session):
        self.db = db

    def get_environments(self) -> Sequence[Environment]:
        return self.db.scalars(select(Environment)).all()

    def create_environment(self, environment: Environment) -> None:
        self.db.add(Environment(**environment.model_dump()))
        self.db.commit()

    def get_environment_platform_service_config(
        self, environment_id: UUID, platform_id: UUID, service_id: UUID
    ) -> EnvPlatformServiceConfig:
        stmt = select(EnvPlatformServiceConfig).where(
            EnvPlatformServiceConfig.environment_id == environment_id,
            EnvPlatformServiceConfig.platform_id == platform_id,
            EnvPlatformServiceConfig.service_id == service_id,
        )
        return self.db.scalar(stmt)

    def get_environment_platform_config(
        self, environment_id: UUID, platform_id: UUID
    ) -> EnvPlatformConfig:
        stmt = select(EnvPlatformConfig).where(
            EnvPlatformConfig.environment_id == environment_id,
            EnvPlatformConfig.platform_id == platform_id,
        )
        return self.db.scalar(stmt)

    def get_environment_configs(
        self, environment_id: UUID
    ) -> Sequence[EnvPlatformServiceConfig]:
        stmt = select(EnvPlatformServiceConfig).where(
            EnvPlatformServiceConfig.environment_id == environment_id
        )
        return self.db.scalars(stmt).all()
