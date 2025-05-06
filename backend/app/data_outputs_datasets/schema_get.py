from datetime import datetime
from typing import Optional
from uuid import UUID

from app.data_outputs.schema_basic import DataOutputBasic
from app.datasets.schema_basic import DatasetBasic
from app.role_assignments.enums import DecisionStatus
from app.shared.schema import ORMModel
from app.users.schema import User


class BaseDataOutputDatasetAssociationGet(ORMModel):
    id: UUID
    dataset_id: UUID
    data_output_id: UUID
    status: DecisionStatus
    requested_on: datetime
    denied_on: Optional[datetime]
    approved_on: Optional[datetime]

    # Nested schemas
    dataset: DatasetBasic
    data_output: DataOutputBasic
    requested_by: User
    denied_by: Optional[User]
    approved_by: Optional[User]


class DataOutputDatasetAssociationGet(BaseDataOutputDatasetAssociationGet):
    pass


class DataOutputDatasetAssociationsGet(BaseDataOutputDatasetAssociationGet):
    pass
