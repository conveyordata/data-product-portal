from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from app.data_products_datasets.model import DataProductDatasetAssociation
from app.notifications.base_model import BaseNotificationConfiguration


class DataProductDatasetNotification(BaseNotificationConfiguration):
    data_product_dataset_id: Mapped[UUID] = Column(
        ForeignKey("data_products_datasets.id")
    )
    data_product_dataset: Mapped["DataProductDatasetAssociation"] = relationship()
    __mapper_args__ = {
        "polymorphic_identity": "DataProductDataset",
    }
