from datetime import datetime
from typing import Optional
from uuid import UUID

from app.authorization.role_assignments.enums import DecisionStatus
from app.data_products.schema import DataProduct
from app.datasets.schema import Dataset
from app.shared.schema import ORMModel
from app.users.schema import User


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


class DataProductDatasetAssociationGet(BaseDataProductDatasetAssociationGet):
    pass


class DataProductDatasetAssociationsGet(BaseDataProductDatasetAssociationGet):
    pass
