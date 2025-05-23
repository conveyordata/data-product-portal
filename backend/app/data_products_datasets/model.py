from typing import TYPE_CHECKING

from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.role_assignments.enums import DecisionStatus

if TYPE_CHECKING:
    from app.users.model import User
    from app.datasets.model import Dataset
    from app.data_products.model import DataProduct

import uuid

from app.shared.model import BaseORM, utcnow


class DataProductDatasetAssociation(Base, BaseORM):
    __tablename__ = "data_products_datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status: Mapped[DecisionStatus] = mapped_column(
        Enum(DecisionStatus),
        default=DecisionStatus.PENDING,
    )
    requested_on = Column(DateTime(timezone=False), server_default=utcnow())
    approved_on = Column(DateTime(timezone=False))
    denied_on = Column(DateTime(timezone=False))

    # Foreign keys
    data_product_id: Mapped[uuid.UUID] = mapped_column(
        "data_product_id", ForeignKey("data_products.id")
    )
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        "dataset_id", ForeignKey("datasets.id")
    )
    requested_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    approved_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    denied_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    # Relationships
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="data_product_links",
        order_by="Dataset.name",
        lazy="joined",
    )
    data_product: Mapped["DataProduct"] = relationship(
        "DataProduct",
        back_populates="dataset_links",
        order_by="DataProduct.name",
        lazy="joined",
    )
    requested_by: Mapped["User"] = relationship(
        foreign_keys=[requested_by_id],
        back_populates="requested_datasets",
        lazy="joined",
    )
    approved_by: Mapped["User"] = relationship(
        foreign_keys=[approved_by_id],
        back_populates="approved_datasets",
        lazy="joined",
    )
    denied_by: Mapped["User"] = relationship(
        foreign_keys=[denied_by_id],
        back_populates="denied_datasets",
        lazy="joined",
    )

    __table_args__ = (
        UniqueConstraint(
            "data_product_id", "dataset_id", name="unique_data_product_dataset"
        ),
    )
