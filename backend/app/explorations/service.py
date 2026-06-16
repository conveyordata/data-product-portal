from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import asc, select
from sqlalchemy.orm import Session, joinedload
from starlette import status

from app.abstract_data_product.service import AbstractDataProductService
from app.core.context import queue_event
from app.core.namespace.validation import NamespaceValidator
from app.core.webhooks.events import ExplorationCreatedEvent, ExplorationPayload
from app.resource_names.service import ResourceNameService, ResourceNameValidityType
from app.users.model import User

from .model import Exploration as ExplorationModel
from .model import ensure_exploration_exists
from .schema_request import CreateExplorationRequest


class ExplorationService(AbstractDataProductService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.namespace_validator = NamespaceValidator(ExplorationModel)

    def create_exploration(
        self,
        exploration: CreateExplorationRequest,
        authenticated_user: User,
    ) -> ExplorationModel:
        if (
            validity := ResourceNameService(model=ExplorationModel)
            .validate_resource_name(exploration.namespace, self.db)
            .validity
        ) != ResourceNameValidityType.VALID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {validity.value}",
            )
        model = ExplorationModel(
            **exploration.parse_pydantic_schema(), owner_id=authenticated_user.id
        )
        self.db.add(model)
        self.db.flush()
        queue_event(ExplorationCreatedEvent(after=model.to_event()))
        return model

    def get_explorations(
        self, filter_to_user_with_assigment: Optional[UUID] = None
    ) -> Sequence[ExplorationModel]:
        query = select(ExplorationModel).order_by(asc(ExplorationModel.name))
        if filter_to_user_with_assigment:
            query = query.where(
                ExplorationModel.owner_id == filter_to_user_with_assigment
            )
        return self.db.scalars(query).unique().all()

    def get_exploration(self, id: UUID, authenticated_user: User) -> ExplorationModel:
        return ensure_exploration_exists(
            id,
            self.db,
            authenticated_user,
            options=[joinedload(ExplorationModel.owner)],
        )
