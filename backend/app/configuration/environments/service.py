from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.configuration.environments.model import (
    ENVIRONMENT_DISPLAY_ORDER,
)
from app.configuration.environments.model import Environment as EnvironmentModel
from app.configuration.environments.schema_request import EnvironmentUpdate
from app.configuration.environments.schema_response import Environment


class EnvironmentService:
    def __init__(self, db: Session):
        self.db = db

    def get_environments(self) -> Sequence[Environment]:
        return self.db.scalars(
            select(EnvironmentModel).order_by(*ENVIRONMENT_DISPLAY_ORDER)
        ).all()

    def get_environment(self, environment_id: UUID) -> Environment:
        return self.db.scalar(select(EnvironmentModel).filter_by(id=environment_id))

    def update_environment(
        self, environment_id: UUID, update: EnvironmentUpdate
    ) -> Environment:
        environment = self._get_or_404(environment_id)
        for field, value in update.model_dump(exclude_unset=True).items():
            setattr(environment, field, value)
        self.db.flush()
        return environment

    def _get_or_404(self, environment_id: UUID) -> EnvironmentModel:
        environment = self.db.scalar(
            select(EnvironmentModel).filter_by(id=environment_id)
        )
        if not environment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found",
            )
        return environment
