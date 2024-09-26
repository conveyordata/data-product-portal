from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.platform_services.model import PlatformService as PlatformServiceModel
from app.platform_services.schema import PlatformService


class PlatformServiceService:
    def __init__(self, db: Session):
        self.db = db

    def get_platform_services(self, platform_id: UUID) -> Sequence[PlatformService]:
        return self.db.scalars(
            select(PlatformServiceModel).filter_by(platform_id=platform_id)
        ).all()
