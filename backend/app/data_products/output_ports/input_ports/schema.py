from uuid import UUID
from warnings import deprecated

from app.authorization.role_assignments.enums import DecisionStatus
from app.shared.schema import ORMModel


class DataProductOutputPortAssociation(ORMModel):
    id: UUID
    justification: str
    data_product_id: UUID
    output_port_id: UUID
    status: DecisionStatus


@deprecated("Use DataProductOutputPortAssociation instead")
class DataProductDatasetAssociation(ORMModel):
    id: UUID
    justification: str
    data_product_id: UUID
    dataset_id: UUID
    status: DecisionStatus
