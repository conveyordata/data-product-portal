from typing import Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.configuration.platforms.model import Platform as PlatformModel
from app.configuration.platforms.schema_response import Platform
from app.database.deps import get_db_session


class PlatformService:
    def __init__(self, db: Session = Depends(get_db_session)):
        self.db = db

    def get_all_platforms(self) -> Sequence[Platform]:
        return self.db.scalars(select(PlatformModel)).all()
