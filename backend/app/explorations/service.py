from typing import Sequence
from uuid import UUID

from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.abstract_data_product.service import AbstractDataProductService
from app.core.namespace.validation import NamespaceValidator

from .model import Exploration as ExplorationModel
from .schema_request import CreateExplorationRequest


class ExplorationService(AbstractDataProductService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.namespace_validator = NamespaceValidator(ExplorationModel)

    def create_exploration(
        self,
        exploration: CreateExplorationRequest,
    ) -> ExplorationModel:
        model = ExplorationModel(**exploration.parse_pydantic_schema())
        self.db.add(model)
        self.db.flush()
        return model

    def get_explorations(self) -> Sequence[ExplorationModel]:
        query = select(ExplorationModel).order_by(asc(ExplorationModel.name))
        return self.db.scalars(query).unique().all()

    def get_exploration(self, id: UUID) -> type[ExplorationModel] | None:
        return self.db.get(ExplorationModel, id)
