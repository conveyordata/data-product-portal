from typing import TYPE_CHECKING

from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus
from app.database.database import Base

if TYPE_CHECKING:
    from app.users.model import User
    from app.datasets.model import Dataset
    from app.data_outputs.model import DataOutput

import uuid

from app.shared.model import BaseORM, utcnow


class DataOutputDatasetAssociation(Base, BaseORM):
    __tablename__ = "data_outputs_datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status: Mapped[DataOutputDatasetLinkStatus] = mapped_column(
        Enum(DataOutputDatasetLinkStatus),
        default=DataOutputDatasetLinkStatus.PENDING_APPROVAL,
    )
    requested_on = Column(DateTime(timezone=False), server_default=utcnow())
    approved_on = Column(DateTime(timezone=False))
    denied_on = Column(DateTime(timezone=False))

    # Foreign keys
    data_output_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("data_outputs.id"))
    dataset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("datasets.id"))
    requested_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    approved_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    denied_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    # Relationships
    data_output: Mapped["DataOutput"] = relationship(
        back_populates="dataset_links",
        order_by="DataOutput.name",
        lazy="joined",
    )
    dataset: Mapped["Dataset"] = relationship(
        back_populates="data_output_links",
        order_by="Dataset.name",
        lazy="joined",
    )
    requested_by: Mapped["User"] = relationship(
        foreign_keys=[requested_by_id],
        back_populates="requested_dataoutputs",
        lazy="joined",
    )
    approved_by: Mapped["User"] = relationship(
        foreign_keys=[approved_by_id],
        back_populates="approved_dataoutputs",
        lazy="joined",
    )
    denied_by: Mapped["User"] = relationship(
        foreign_keys=[denied_by_id], back_populates="denied_dataoutputs", lazy="joined"
    )

    __table_args__ = (
        UniqueConstraint(
            "data_output_id", "dataset_id", name="unique_data_output_dataset"
        ),
    )
