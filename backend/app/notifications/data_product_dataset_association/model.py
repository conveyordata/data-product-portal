from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped

from app.notifications.base_model import BaseNotificationConfiguration


class DataProductDatasetNotification(BaseNotificationConfiguration):
    data_product_dataset_id: Mapped[UUID] = Column(
        ForeignKey("data_products_datasets.id")
    )
    __mapper_args__ = {
        "polymorphic_identity": "DataProductDataset",
    }
