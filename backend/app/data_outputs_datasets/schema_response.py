from datetime import datetime
from typing import Optional
from uuid import UUID

from app.data_outputs.schema import DataOutput as DataOutputBaseSchema
from app.data_products.schema import DataProduct
from app.datasets.schema import Dataset
from app.role_assignments.enums import DecisionStatus
from app.shared.schema import ORMModel
from app.users.schema import User


class DataOutput(DataOutputBaseSchema):
    # Nested schemas
    owner: DataProduct


class BaseDataOutputDatasetAssociationGet(ORMModel):
    id: UUID
    dataset_id: UUID
    data_output_id: UUID
    status: DecisionStatus
    requested_on: datetime
    denied_on: Optional[datetime]
    approved_on: Optional[datetime]

    # Nested schemas
    dataset: Dataset
    data_output: DataOutput
    requested_by: User
    denied_by: Optional[User]
    approved_by: Optional[User]


class DataOutputDatasetAssociationGet(BaseDataOutputDatasetAssociationGet):
    pass


class DataOutputDatasetAssociationsGet(BaseDataOutputDatasetAssociationGet):
    pass
