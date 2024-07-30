from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.platforms.models import Platform
from app.platforms.models import PlatformService as PlatformServiceModel
from app.platforms.models import PlatformServiceConfig


class PlatformsService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_platforms(self) -> Sequence[Platform]:
        return self.db.scalars(select(Platform)).all()

    def get_platform_services(
        self, platform_id: UUID
    ) -> Sequence[PlatformServiceModel]:
        return self.db.scalars(
            select(PlatformServiceModel).filter_by(platform_id=platform_id)
        ).all()

    def get_service_config(self, platform_id, service_id):
        return self.db.scalar(
            select(PlatformServiceConfig.config).filter_by(
                platform_id=platform_id, service_id=service_id
            )
        )
