from typing import Sequence

from sqlalchemy import select

from app.configuration.platforms.model import Platform as PlatformModel
from app.configuration.platforms.schema_response import Platform
from app.database.deps import DbSession


class PlatformService:
    def __init__(self, db: DbSession):
        self.db = db

    def get_all_platforms(self) -> Sequence[Platform]:
        return self.db.scalars(select(PlatformModel)).all()
