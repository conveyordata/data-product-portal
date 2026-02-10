from uuid import UUID
from warnings import deprecated

from app.authorization.role_assignments.enums import DecisionStatus
from app.configuration.data_product_types.schema import DataProductType
from app.shared.schema import ORMModel


class DataProductInfo(ORMModel):
    name: str
    type: DataProductType


class DataProductOutputPortAssociation(ORMModel):
    id: UUID
    justification: str
    data_product_id: UUID
    data_product: DataProductInfo
    output_port_id: UUID
    status: DecisionStatus


@deprecated("Use DataProductOutputPortAssociation instead")
class DataProductDatasetAssociation(ORMModel):
    id: UUID
    justification: str
    data_product_id: UUID
    data_product: DataProductInfo
    dataset_id: UUID
    status: DecisionStatus
