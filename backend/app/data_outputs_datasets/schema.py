from datetime import datetime
from uuid import UUID

from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus
from app.data_outputs_datasets.model import (
    DataOutputDatasetAssociation as DataOutputDatasetModel,
)
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
    status: DataOutputDatasetLinkStatus
    requested_by: User
    denied_by: User | None
    approved_by: User | None
    requested_on: datetime
    denied_on: datetime | None
    approved_on: datetime | None
