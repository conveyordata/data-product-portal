from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.data_products.output_ports.semantic_models.model import OutputPortSemanticModel
from app.data_products.output_ports.semantic_models.schema_request import (
    SemanticModelRequest,
)


class SemanticModelService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, output_port_id: UUID) -> list[OutputPortSemanticModel]:
        return (
            self.db.query(OutputPortSemanticModel)
            .filter(OutputPortSemanticModel.output_port_id == output_port_id)
            .order_by(OutputPortSemanticModel.name)
            .all()
        )

    def create(
        self, output_port_id: UUID, request: SemanticModelRequest
    ) -> OutputPortSemanticModel:
        model = OutputPortSemanticModel(
            output_port_id=output_port_id,
            name=request.name,
            format=request.format,
            content=request.content,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def replace(
        self, model_id: UUID, request: SemanticModelRequest
    ) -> OutputPortSemanticModel:
        model = self._get_or_404(model_id)
        model.name = request.name
        model.format = request.format
        model.content = request.content
        self.db.commit()
        self.db.refresh(model)
        return model

    def delete(self, model_id: UUID) -> None:
        model = self._get_or_404(model_id)
        self.db.delete(model)
        self.db.commit()

    def _get_or_404(self, model_id: UUID) -> OutputPortSemanticModel:
        model = self.db.get(OutputPortSemanticModel, model_id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Semantic model {model_id} not found",
            )
        return model
