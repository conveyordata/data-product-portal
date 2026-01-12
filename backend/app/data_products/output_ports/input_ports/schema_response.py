from datetime import datetime
from typing import Optional
from uuid import UUID
from warnings import deprecated

from app.authorization.role_assignments.enums import DecisionStatus
from app.data_products.output_ports.schema import Dataset, OutputPort
from app.data_products.schema import DataProduct
from app.shared.schema import ORMModel
from app.users.schema import User


class BaseDataProductOutputPortAssociationGet(ORMModel):
    id: UUID
    justification: str
    data_product_id: UUID
    output_port_id: UUID
    status: DecisionStatus
    requested_on: datetime

    # Nested schemas
    output_port: OutputPort
    data_product: DataProduct
    requested_by: User
    denied_by: Optional[User]
    approved_by: Optional[User]


@deprecated("Use BaseDataProductOutputPortAssociationGet instead")
class BaseDataProductDatasetAssociationGet(ORMModel):
    id: UUID
    justification: str
    data_product_id: UUID
    dataset_id: UUID
    status: DecisionStatus
    requested_on: datetime

    # Nested schemas
    dataset: Dataset
    data_product: DataProduct
    requested_by: User
    denied_by: Optional[User]
    approved_by: Optional[User]

    def convert(self) -> BaseDataProductOutputPortAssociationGet:
        base = self.model_dump(exclude={"dataset_id", "dataset"})
        return BaseDataProductOutputPortAssociationGet(
            **base,
            output_port_id=self.dataset_id,
            output_port=self.dataset.convert(),
        )


class DataProductDatasetAssociationGet(BaseDataProductDatasetAssociationGet):
    pass


class DataProductDatasetAssociationsGet(BaseDataProductDatasetAssociationGet):
    pass


class DataProductOutputPortAssociationsGet(BaseDataProductOutputPortAssociationGet):
    pass
