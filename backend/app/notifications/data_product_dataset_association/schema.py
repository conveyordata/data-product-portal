from typing import Literal
from uuid import UUID

from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.notifications.data_product_dataset_association.model import (
    DataProductDatasetNotification as DataProductDatasetNotificationModel,
)
from app.notifications.notification_types import NotificationTypes
from app.notifications.schema import Notification


class DataProductDatasetNotification(Notification):
    data_product_dataset_id: UUID
    data_product_dataset: DataProductDatasetAssociation
    configuration_type: Literal[NotificationTypes.DataProductDatasetNotification]

    class Meta:
        orm_model = DataProductDatasetNotificationModel
