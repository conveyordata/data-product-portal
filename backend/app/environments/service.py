from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.environments.model import Environment, EnvPlatformServiceConfig
from app.environments.schema import Config
from app.exceptions import NotFoundInDB
from app.platforms.models import PlatformServiceConfig
from app.platforms.schemas import PlatformServiceConfigSchema


class EnvironmentService:
    def __init__(self, db: Session):
        self.db = db

    def get_environments(self) -> Sequence[Environment]:
        return self.db.scalars(select(Environment)).all()

    def create_environment(self, environment: Environment) -> None:
        self.db.add(Environment(**environment.model_dump()))
        self.db.commit()

    def get_config(
        self, environment_id: UUID, platform_id: UUID, service_id: UUID
    ) -> str:
        stmt = select(EnvPlatformServiceConfig.config).where(
            EnvPlatformServiceConfig.environment_id == environment_id,
            EnvPlatformServiceConfig.platform_id == platform_id,
            EnvPlatformServiceConfig.service_id == service_id,
        )
        return self.db.scalar(stmt)

    def create_config(
        self, environment_id: UUID, platform_id: UUID, service_id: UUID, config: Config
    ):
        # Check if config contains configuration for all the identifiers
        stmt = select(PlatformServiceConfig.config).where(
            PlatformServiceConfig.platform_id == platform_id,
            PlatformServiceConfig.service_id == service_id,
        )

        platform_service_config = self.db.scalar(stmt)
        if not platform_service_config:
            raise NotFoundInDB("There's no platform service configuration")

        identifiers = PlatformServiceConfigSchema(
            config=platform_service_config
        ).config.identifiers
        if set(identifiers) != set(config.dict()):
            raise ValueError("Invalid configuration")

        self.db.add(
            EnvPlatformServiceConfig(
                environment_id=environment_id,
                platform_id=platform_id,
                service_id=service_id,
                config=config.model_dump_json(),
            )
        )
        self.db.flush()
