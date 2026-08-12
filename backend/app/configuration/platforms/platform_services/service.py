from typing import Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.configuration.platforms.platform_services.model import (
    PlatformService as PlatformServiceModel,
)
from app.configuration.platforms.platform_services.schema import PlatformService
from app.database.database import get_db_session


class PlatformServiceService:
    def __init__(self, db: Session = Depends(get_db_session)):
        self.db = db

    def get_platform_services(self, platform_id: UUID) -> Sequence[PlatformService]:
        return self.db.scalars(
            select(PlatformServiceModel).filter_by(platform_id=platform_id)
        ).all()
