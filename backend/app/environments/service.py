import json
from typing import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.environments.model import Environment, EnvPlatformServiceConfig
from app.environments.schema import Config
from app.environments.schema import Environment as EnvironmentSchema
from app.environments.schema import (
    EnvironmentsConfigurations,
    EnvironmentSetting,
    PlatformConfig,
)
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

    def create_environment(self, environment: EnvironmentSchema) -> None:
        self.db.add(Environment(**environment.model_dump()))
        self.db.commit()

    def get_environment_configs(
        self, environment_id: UUID
    ) -> Sequence[EnvPlatformServiceConfig]:
        stmt = select(EnvPlatformServiceConfig).where(
            EnvPlatformServiceConfig.environment_id == environment_id
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

    @staticmethod
    def validate_configurations(configurations: EnvironmentsConfigurations):
        set_identifiers = {}
        for platform in configurations.platforms:
            for service in platform.services:
                identifiers = service.identifiers
                if len(identifiers) != len(set(identifiers)):
                    raise ValueError("Duplicated identifiers")

                set_identifiers[(platform.id, service.id)] = set(identifiers)

        for environment in configurations.environments:
            for setting in environment.settings:
                configured_identifiers = set()
                for config in setting.configs:
                    configured_identifiers.add(config.identifier)

                if configured_identifiers != set_identifiers.get(
                    (setting.platform_id, setting.service_id)
                ):
                    raise ValueError(
                        f"Incorrect set of identifiers is configured "
                        f"for {setting.platform_name}/{setting.service_name}"
                    )

    def create_platform_service_configs(self, platforms: list[PlatformConfig]):
        platform_service_objs = []
        for platform in platforms:
            for service in platform.services:
                if platform_service_config := self.db.scalar(
                    select(PlatformServiceConfig).where(
                        PlatformServiceConfig.platform_id == platform.id,
                        PlatformServiceConfig.service_id == service.id,
                    )
                ):
                    platform_service_config.config = json.dumps(service.identifiers)

                else:
                    platform_service_config = PlatformServiceConfig(
                        platform_id=platform.id,
                        service_id=service.id,
                        config=json.dumps(service.identifiers),
                    )

                platform_service_objs.append(platform_service_config)

        self.db.bulk_save_objects(platform_service_objs)
        self.db.flush()

    def create_environments(self, environments: list[EnvironmentSetting]):
        existing_environments = {
            env.name: env for env in self.db.scalars(select(Environment)).all()
        }

        for environment in environments:
            environment_obj = existing_environments.pop(
                environment.name, Environment(name=environment.name)
            )

            env_configs = {
                (config.platform_id, config.service_id): config
                for config in environment_obj.env_platform_service_configs
            }

            new_env_configs = []
            for setting in environment.settings:
                new_config = env_configs.pop(
                    (setting.platform_id, setting.service_id),
                    EnvPlatformServiceConfig(
                        platform_id=setting.platform_id, service_id=setting.service_id
                    ),
                )
                new_config.config = json.dumps(
                    setting.model_dump(include={"configs"})["configs"]
                )
                new_env_configs.append(new_config)

            environment_obj.env_platform_service_configs = new_env_configs
            self.db.add(environment_obj)

        if existing_environments:
            self.db.execute(
                delete(Environment).where(
                    Environment.id.in_(env.id for env in existing_environments.values())
                )
            )

    def save_environments_configurations(
        self, configurations: EnvironmentsConfigurations
    ):
        self.validate_configurations(configurations)
        self.create_platform_service_configs(configurations.platforms)
        self.create_environments(configurations.environments)
