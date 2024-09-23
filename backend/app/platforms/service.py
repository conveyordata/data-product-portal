from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.platform_service_configurations.model import (
    PlatformServiceConfiguration as PlatformServiceConfigurationModel,
)
from app.platform_service_configurations.schema import PlatformServiceConfiguration
from app.platform_services.model import PlatformService as PlatformServiceModel
from app.platform_services.schema import PlatformService
from app.platforms.model import Platform as PlatformModel
from app.platforms.schema import Platform


class PlatformsService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_platforms(self) -> Sequence[Platform]:
        return self.db.scalars(select(PlatformModel)).all()

    def get_platform_services(self, platform_id: UUID) -> Sequence[PlatformService]:
        return self.db.scalars(
            select(PlatformServiceModel).filter_by(platform_id=platform_id)
        ).all()

    def get_service_config(
        self, platform_id, service_id
    ) -> PlatformServiceConfiguration:
        return self.db.scalar(
            select(PlatformServiceConfigurationModel).filter_by(
                platform_id=platform_id, service_id=service_id
            )
        )
