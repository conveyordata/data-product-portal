from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from app.data_outputs_datasets.model import DataOutputDatasetAssociation
from app.notifications.model import Notification


class DataOutputDatasetNotification(Notification):
    data_output_dataset_id: Mapped[UUID] = Column(
        ForeignKey("data_outputs_datasets.id")
    )
    data_output_dataset: Mapped["DataOutputDatasetAssociation"] = relationship()
    __mapper_args__ = {
        "polymorphic_identity": "DataOutputDataset",
    }
