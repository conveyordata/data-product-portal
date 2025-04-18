from datetime import datetime
from uuid import UUID

from app.data_outputs.schema_base_get import DataOutputBaseGet
from app.data_outputs_datasets.model import (
    DataOutputDatasetAssociation as DataOutputDatasetModel,
)
from app.datasets.schema import Dataset
from app.role_assignments.enums import DecisionStatus
from app.shared.schema import ORMModel
from app.users.schema import User


class BaseDataOutputDatasetAssociation(ORMModel):
    dataset_id: UUID
    status: DecisionStatus = DecisionStatus("pending")

    class Meta:
        orm_model = DataOutputDatasetModel


class DataOutputDatasetAssociationCreate(BaseDataOutputDatasetAssociation):
    pass


class DataOutputDatasetAssociationUpdate(BaseDataOutputDatasetAssociation):
    pass


class DataOutputDatasetAssociation(BaseDataOutputDatasetAssociation):
    id: UUID
    data_output_id: UUID
    dataset: Dataset
    data_output: DataOutputBaseGet
    status: DecisionStatus
    requested_by: User
    denied_by: User | None
    approved_by: User | None
    requested_on: datetime
    denied_on: datetime | None
    approved_on: datetime | None
