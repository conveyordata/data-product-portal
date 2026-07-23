from typing import Optional
from uuid import UUID

from app.abstract_data_product.input_ports.model import (
    InputPort as DataProductDatasetModel,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.shared.schema import ORMModel


class DataProductDatasetAssociationCreate(ORMModel):
    dataset_id: UUID
    status: DecisionStatus = DecisionStatus.PENDING

    class Meta:
        orm_model = DataProductDatasetModel


class DataProductDatasetAssociationUpdate(DataProductDatasetAssociationCreate):
    pass


class ApproveOutputPortAsInputPortRequest(ORMModel):
    consuming_data_product_id: UUID
    decision_note: Optional[str] = None


class DenyOutputPortAsInputPortRequest(ORMModel):
    consuming_data_product_id: UUID
    decision_note: str


class RevokeOutputPortAsInputPortRequest(ORMModel):
    consuming_data_product_id: UUID


class RemoveOutputPortAsInputPortRequest(ORMModel):
    consuming_data_product_id: UUID
