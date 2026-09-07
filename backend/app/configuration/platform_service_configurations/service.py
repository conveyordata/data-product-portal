from typing import Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.configuration.platform_service_configurations.model import (
    PlatformServiceConfiguration as PlatformServiceConfigurationModel,
)
from app.configuration.platform_service_configurations.schema import (
    PlatformServiceConfiguration,
)
from app.database.deps import get_db_session


class PlatformServiceConfigurationService:
    def __init__(self, db: Session = Depends(get_db_session)):
        self.db = db

    def get_platform_service_configuration(
        self, platform_id, service_id
    ) -> PlatformServiceConfiguration:
        return self.db.scalar(
            select(PlatformServiceConfigurationModel).filter_by(
                platform_id=platform_id, service_id=service_id
            )
        )

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
