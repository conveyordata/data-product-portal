from typing import Literal
from uuid import UUID

from app.notifications.data_output_dataset_association.model import (
    DataOutputDatasetNotification as DataOutputDatasetNotificationModel,
)
from app.notifications.notification_types import NotificationTypes
from app.notifications.schema_base import BaseNotificationConfiguration


class DataOutputDatasetNotification(BaseNotificationConfiguration):
    data_output_dataset_id: UUID
    configuration_type: Literal[NotificationTypes.DataOutputDataset]

    class Meta:
        orm_model = DataOutputDatasetNotificationModel
