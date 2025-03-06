from typing import TYPE_CHECKING

from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data_products_datasets.enums import DataProductDatasetLinkStatus

if TYPE_CHECKING:
    from app.users.model import User
    from app.datasets.model import Dataset
    from app.data_products.model import DataProduct

import uuid

from app.notifications.base_model import BaseNotificationConfiguration
from app.shared.model import utcnow


class DataProductDatasetAssociation(BaseNotificationConfiguration):
    __tablename__ = "data_products_datasets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_product_id: Mapped[uuid.UUID] = mapped_column(
        "data_product_id", ForeignKey("data_products.id")
    )
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        "dataset_id", ForeignKey("datasets.id")
    )
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="data_product_links",
        order_by="Dataset.name",
    )
    data_product: Mapped["DataProduct"] = relationship(
        "DataProduct", back_populates="dataset_links", order_by="DataProduct.name"
    )
    status: Mapped[DataProductDatasetLinkStatus] = mapped_column(
        Enum(DataProductDatasetLinkStatus),
        default=DataProductDatasetLinkStatus.PENDING_APPROVAL,
    )
    requested_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    requested_by: Mapped["User"] = relationship(
        foreign_keys=[requested_by_id], back_populates="requested_datasets"
    )
    requested_on = Column(DateTime(timezone=False), server_default=utcnow())
    approved_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    approved_by: Mapped["User"] = relationship(
        foreign_keys=[approved_by_id], back_populates="approved_datasets"
    )
    approved_on = Column(DateTime(timezone=False))
    denied_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    denied_by: Mapped["User"] = relationship(
        foreign_keys=[denied_by_id], back_populates="denied_datasets"
    )
    denied_on = Column(DateTime(timezone=False))
    __table_args__ = (
        UniqueConstraint(
            "data_product_id", "dataset_id", name="unique_data_product_dataset"
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": "DataProductDatasetAssociation",
    }
