from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.configuration.platforms.model import Platform as PlatformModel
from app.configuration.platforms.schema_response import Platform


class PlatformService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_platforms(self) -> Sequence[Platform]:
        return self.db.scalars(select(PlatformModel)).all()
