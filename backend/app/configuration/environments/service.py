from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.configuration.environments.model import Environment as EnvironmentModel
from app.configuration.environments.schema_response import Environment


class EnvironmentService:
    def __init__(self, db: Session):
        self.db = db

    def get_environments(self) -> Sequence[Environment]:
        return self.db.scalars(select(EnvironmentModel)).all()

    def get_environment(self, environment_id: UUID) -> Environment:
        return self.db.scalar(select(EnvironmentModel).filter_by(id=environment_id))

    def update_is_global(self, environment_id: UUID, is_global: bool) -> Environment:
        environment = self.db.scalar(
            select(EnvironmentModel).filter_by(id=environment_id)
        )
        if not environment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found",
            )

        environment.is_global = is_global
        self.db.commit()
        return environment
