from pathlib import Path
from uuid import UUID

import yaml
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.environment_platform_configurations.model import (
    EnvironmentPlatformConfiguration as EnvironmentPlatformConfigurationModel,
)
from app.environments.model import Environment as EnvironmentModel
from app.platforms.model import Platform as PlatformModel
from app.users.schema import User
from app.utils.import_helper import import_from_dotted_path
from app.utils.singleton import Singleton


class IntegrationProvider(metaclass=Singleton):
    def __init__(self, db: Session):
        self.db = db
        self.INTEGRATION_PROVIDERS: dict[str, type[IntegrationProvider]] = {}
        self.load_integration_providers()

    def load_integration_providers(self):
        with open(
            Path(__file__).parent.parent.parent / "data_output_registry.yaml"
        ) as f:
            raw_config = yaml.safe_load(f)

        for key, config in raw_config.items():
            provider_path = config.get("provider")
            if provider_path:
                cls = import_from_dotted_path(provider_path)
                self.INTEGRATION_PROVIDERS[key.lower()] = cls

    def generate_url(self, id: UUID, environment: str, actor: User) -> str:
        raise NotImplementedError(
            "IntegrationProvider.generate_url must be implemented in subclasses"
        )

    def get_env_platform_config(
        self, id: UUID, environment: str, platform_name: str
    ) -> str:
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
