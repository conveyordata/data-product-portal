from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.environments.model import Environment, EnvPlatformServiceConfig
from app.environments.schema import Config, EnvPlatformServiceConfigGet
from app.exceptions import NotFoundInDB
from app.platforms.models import PlatformServiceConfig
from app.platforms.schemas import PlatformServiceConfigBaseSchema


class EnvironmentService:
    def __init__(self, db: Session):
        self.db = db

    def get_environments(self) -> Sequence[Environment]:
        return self.db.scalars(select(Environment)).all()

    def get_environment_by_id(self, environment_id: UUID) -> Environment:
        return self.db.scalar(
            select(Environment).where(Environment.id == environment_id)
        )

    def create_environment(self, environment: Environment) -> None:
        self.db.add(Environment(**environment.model_dump()))
        self.db.commit()

    def get_environment_configs(
        self, environment_id: UUID
    ) -> Sequence[EnvPlatformServiceConfig]:
        stmt = select(EnvPlatformServiceConfig).where(
            EnvPlatformServiceConfig.environment_id == environment_id
        )
        return self.db.scalars(stmt).all()

    def get_environment_config(
        self, platform_id: UUID, service_id: UUID
    ) -> Sequence[EnvPlatformServiceConfigGet]:
        print("Called")
        stmt = select(EnvPlatformServiceConfig).where(
            EnvPlatformServiceConfig.platform_id == platform_id,
            EnvPlatformServiceConfig.service_id == service_id,
        )
        return self.db.scalars(stmt).all()

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

        identifiers = PlatformServiceConfigBaseSchema(
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
        try:
            self.db.flush()
        except IntegrityError:
            raise ValueError("Such configuration already exists")

    def get_environment_config_by_id(self, config_id: UUID):
        return self.db.scalar(
            select(EnvPlatformServiceConfig).where(
                EnvPlatformServiceConfig.id == config_id
            )
        )
