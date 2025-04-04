from datetime import datetime
from typing import Optional
from uuid import UUID

from app.data_outputs.schema_base_get import DataOutputBaseGet
from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus
from app.data_outputs_datasets.model import (
    DataOutputDatasetAssociation as DataOutputDatasetModel,
)
from app.datasets.schema import Dataset
from app.shared.schema import ORMModel
from app.users.schema import User


class BaseDataOutputDatasetAssociation(ORMModel):
    dataset_id: UUID
    status: DataOutputDatasetLinkStatus = DataOutputDatasetLinkStatus.PENDING_APPROVAL

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
    status: DataOutputDatasetLinkStatus
    requested_by: User
    denied_by: Optional[User]
    approved_by: Optional[User]
    requested_on: datetime
    denied_on: Optional[datetime]
    approved_on: Optional[datetime]
