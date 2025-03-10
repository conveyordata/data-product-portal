from typing import Literal
from uuid import UUID

from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.notifications.data_product_dataset_association.model import (
    DataProductDatasetNotification as DataProductDatasetNotificationModel,
)
from app.notifications.notification_types import NotificationTypes
from app.notifications.schema_base import BaseNotificationConfiguration


class DataProductDatasetNotificationGet(BaseNotificationConfiguration):
    data_product_dataset_id: UUID
    data_product_dataset: DataProductDatasetAssociation
    configuration_type: Literal[NotificationTypes.DataProductDataset]

    class Meta:
        orm_model = DataProductDatasetNotificationModel
