from typing import Literal
from uuid import UUID

from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.notifications.data_output_dataset_association.model import (
    DataOutputDatasetNotification as DataOutputDatasetNotificationModel,
)
from app.notifications.notification_types import NotificationTypes
from app.notifications.schema_base import BaseNotificationConfiguration


class DataOutputDatasetNotificationGet(BaseNotificationConfiguration):
    data_output_dataset_id: UUID
    data_output_dataset: DataOutputDatasetAssociation
    configuration_type: Literal[NotificationTypes.DataOutputDataset]

    class Meta:
        orm_model = DataOutputDatasetNotificationModel
