from uuid import UUID

from app.role_assignments.enums import DecisionStatus
from app.shared.schema import ORMModel


class DataProductDatasetAssociationBasic(ORMModel):
    id: UUID
    data_product_id: UUID
    dataset_id: UUID
    status: DecisionStatus
