from datetime import datetime
from typing import Literal
from uuid import UUID

from app.data_outputs.schema_base_get import DataOutputBaseGet
from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus
from app.data_outputs_datasets.model import (
    DataOutputDatasetAssociation as DataOutputDatasetModel,
)
from app.datasets.schema import Dataset
from app.notifications.notification_types import NotificationTypes
from app.notifications.schema_base import BaseNotificationConfiguration
from app.users.schema import User


class BaseDataOutputDatasetAssociation(BaseNotificationConfiguration):
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
    denied_by: User | None
    approved_by: User | None
    requested_on: datetime
    denied_on: datetime | None
    approved_on: datetime | None
    configuration_type: Literal[NotificationTypes.DataOutputDatasetAssociation]
