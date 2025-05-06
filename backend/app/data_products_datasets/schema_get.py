from datetime import datetime
from typing import Optional
from uuid import UUID

from app.data_products.schema_basic import DataProductBasic
from app.datasets.schema_basic import DatasetBasic
from app.role_assignments.enums import DecisionStatus
from app.shared.schema import ORMModel
from app.users.schema import User


class BaseDataProductDatasetAssociationGet(ORMModel):
    id: UUID
    data_product_id: UUID
    dataset_id: UUID
    status: DecisionStatus
    requested_on: datetime

    # Nested schemas
    dataset: DatasetBasic
    data_product: DataProductBasic
    requested_by: User
    denied_by: Optional[User]
    approved_by: Optional[User]


class DataProductDatasetAssociationGet(BaseDataProductDatasetAssociationGet):
    pass


class DataProductDatasetAssociationsGet(BaseDataProductDatasetAssociationGet):
    pass
