from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from app.data_products_datasets.model import DataProductDatasetAssociation
from app.notifications.model import Notification


class DataProductDatasetNotification(Notification):
    data_product_dataset_id: Mapped[UUID] = Column(
        ForeignKey("data_products_datasets.id")
    )
    data_product_dataset: Mapped["DataProductDatasetAssociation"] = relationship(
        "DataProductDatasetAssociation", foreign_keys=[data_product_dataset_id]
    )
    __mapper_args__ = {
        "polymorphic_identity": "DataProductDatasetNotification",
    }
