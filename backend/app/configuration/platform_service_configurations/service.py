from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select

from app.configuration.platform_service_configurations.model import (
    PlatformServiceConfiguration as PlatformServiceConfigurationModel,
)
from app.configuration.platform_service_configurations.schema import (
    PlatformServiceConfiguration,
)
from app.database.deps import DbSession


class PlatformServiceConfigurationService:
    def __init__(self, db: DbSession):
        self.db = db

    def get_platform_service_configuration(
        self, platform_id, service_id
    ) -> PlatformServiceConfiguration:
        service_config = self.db.scalar(
            select(PlatformServiceConfigurationModel).filter_by(
                platform_id=platform_id, service_id=service_id
            )
        )
        if not service_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Platform service configuration not found",
            )
        return service_config

    def get_all_platform_service_configurations(
        self,
    ) -> Sequence[PlatformServiceConfiguration]:
        return self.db.scalars(select(PlatformServiceConfigurationModel)).all()

    def get_single_platform_service_configuration(
        self, config_id: UUID
    ) -> PlatformServiceConfiguration:
        return self.db.scalar(
            select(PlatformServiceConfigurationModel).filter_by(id=config_id)
        )
