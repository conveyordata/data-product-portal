from datetime import datetime
from typing import Literal
from uuid import UUID

from app.data_products.schema_base_get import BaseDataProductGet
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetModel,
)
from app.datasets.schema import Dataset
from app.notifications.notification_types import NotificationTypes
from app.notifications.schema_base import BaseNotificationConfiguration
from app.users.schema import User


class BaseDataProductDatasetAssociation(BaseNotificationConfiguration):
    dataset_id: UUID
    status: DataProductDatasetLinkStatus = DataProductDatasetLinkStatus.PENDING_APPROVAL

    class Meta:
        orm_model = DataProductDatasetModel


class DataProductDatasetAssociationCreate(BaseDataProductDatasetAssociation):
    pass


class DataProductDatasetAssociationUpdate(BaseDataProductDatasetAssociation):
    pass


class DataProductDatasetAssociation(BaseDataProductDatasetAssociation):
    id: UUID
    data_product_id: UUID
    dataset: Dataset
    data_product: BaseDataProductGet
    status: DataProductDatasetLinkStatus
    requested_by: User
    denied_by: User | None
    approved_by: User | None
    requested_on: datetime
    denied_on: datetime | None
    approved_on: datetime | None
    configuration_type: Literal[NotificationTypes.DataProductDataset]


class DatasetDataProductLink(DataProductDatasetAssociation):
    dataset: Dataset
