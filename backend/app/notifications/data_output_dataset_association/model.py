from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped

from app.notifications.base_model import BaseNotificationConfiguration


class DataOutputDatasetNotification(BaseNotificationConfiguration):
    data_output_dataset_id: Mapped[UUID] = Column(
        ForeignKey("data_outputs_datasets.id")
    )
    __mapper_args__ = {
        "polymorphic_identity": "DataOutputDataset",
    }
