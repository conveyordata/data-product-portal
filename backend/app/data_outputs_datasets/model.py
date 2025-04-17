from typing import TYPE_CHECKING

from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus
from app.database.database import Base
from app.notifications.model import DataOutputDatasetNotification

if TYPE_CHECKING:
    from app.users.model import User
    from app.datasets.model import Dataset
    from app.data_outputs.model import DataOutput

import uuid

from app.shared.model import BaseORM, utcnow


class DataOutputDatasetAssociation(Base, BaseORM):
    __tablename__ = "data_outputs_datasets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_output_id: Mapped[uuid.UUID] = mapped_column(
        "data_output_id", ForeignKey("data_outputs.id")
    )
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        "dataset_id", ForeignKey("datasets.id")
    )
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="data_output_links",
        order_by="Dataset.name",
    )
    data_output: Mapped["DataOutput"] = relationship(
        "DataOutput", back_populates="dataset_links", order_by="DataOutput.name"
    )
    status: Mapped[DataOutputDatasetLinkStatus] = mapped_column(
        Enum(DataOutputDatasetLinkStatus),
        default=DataOutputDatasetLinkStatus.PENDING_APPROVAL,
    )
    requested_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    requested_by: Mapped["User"] = relationship(
        foreign_keys=[requested_by_id], back_populates="requested_dataoutputs"
    )
    requested_on = Column(DateTime(timezone=False), server_default=utcnow())
    approved_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    approved_by: Mapped["User"] = relationship(
        foreign_keys=[approved_by_id], back_populates="approved_dataoutputs"
    )
    approved_on = Column(DateTime(timezone=False))
    denied_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    denied_by: Mapped["User"] = relationship(
        foreign_keys=[denied_by_id], back_populates="denied_dataoutputs"
    )
    denied_on = Column(DateTime(timezone=False))
    notifications = relationship(
        DataOutputDatasetNotification,
        cascade="all, delete-orphan",
        passive_deletes=True,
        back_populates="data_output_dataset",
    )
    __table_args__ = (
        UniqueConstraint(
            "data_output_id", "dataset_id", name="unique_data_output_dataset"
        ),
    )
