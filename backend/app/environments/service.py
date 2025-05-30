from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.environments.model import Environment as EnvironmentModel
from app.environments.schema import Environment


class EnvironmentService:
    def __init__(self, db: Session):
        self.db = db

    def get_environments(self) -> Sequence[Environment]:
        return self.db.scalars(select(EnvironmentModel)).all()

    def get_environment(self, environment_id: UUID) -> Environment:
        return self.db.scalar(select(EnvironmentModel).filter_by(id=environment_id))
