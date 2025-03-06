from typing import Literal
from uuid import UUID

from app.notifications.data_product_dataset_association.model import (
    DataProductDatasetNotification as DataProductDatasetNotificationModel,
)
from app.notifications.notification_types import NotificationTypes
from app.notifications.schema_base import BaseNotificationConfiguration


class DataProductDatasetNotification(BaseNotificationConfiguration):
    data_product_dataset_id: UUID
    configuration_type: Literal[NotificationTypes.DataProductDataset]

    class Meta:
        orm_model = DataProductDatasetNotificationModel
