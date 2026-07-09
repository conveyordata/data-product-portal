from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.authorization.role_assignments.enums import DecisionStatus
from app.core.webhooks.events import (
    InputPortEvent,
)
from app.database.database import Base
from app.database.event_mixin import EventTrackedMixin
from app.settings import settings

if TYPE_CHECKING:
    from app.abstract_data_product.model import AbstractDataProduct
    from app.data_products.output_ports.model import Dataset
    from app.users.model import User

import uuid

from app.shared.model import BaseORM, utcnow


class InputPort(
    Base,
    BaseORM,
    EventTrackedMixin,
):
    __tablename__ = "input_ports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    justification = Column(String)
    status: Mapped[DecisionStatus] = mapped_column(
        Enum(DecisionStatus),
        default=DecisionStatus.PENDING,
    )
    requested_on = Column(DateTime(timezone=False), server_default=utcnow())
    approved_on = Column(DateTime(timezone=False))
    denied_on = Column(DateTime(timezone=False))
    renewed_on = Column(DateTime(timezone=False))
    expired_on = Column(DateTime(timezone=False))
    is_renewing = Column(Boolean, nullable=False, default=False)

    requested_duration_days = Column(Integer, nullable=True)
    expires_on = Column(DateTime(timezone=False))
    total_range_start = Column(DateTime(timezone=False))
    total_range_end = Column(DateTime(timezone=False))

    # Foreign keys
    consuming_abstract_data_product_id: Mapped[uuid.UUID] = mapped_column(
        "consuming_abstract_data_product_id", ForeignKey("abstract_data_products.id")
    )
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        "dataset_id", ForeignKey("datasets.id")
    )
    requested_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    approved_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    denied_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    renewed_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    # Relationships
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="data_product_links",
        order_by="Dataset.name",
        lazy="joined",
    )
    consuming_abstract_data_product: Mapped["AbstractDataProduct"] = relationship(
        "AbstractDataProduct",
        back_populates="input_ports",
        order_by="AbstractDataProduct.name",
        lazy="joined",
    )
    requested_by: Mapped["User"] = relationship(
        foreign_keys=[requested_by_id],
        back_populates="requested_input_ports",
        lazy="joined",
    )
    approved_by: Mapped["User"] = relationship(
        foreign_keys=[approved_by_id],
        back_populates="approved_input_ports",
        lazy="joined",
    )
    denied_by: Mapped["User"] = relationship(
        foreign_keys=[denied_by_id],
        back_populates="denied_input_ports",
        lazy="joined",
    )
    renewed_by: Mapped["User"] = relationship(
        foreign_keys=[renewed_by_id],
        back_populates="renewed_input_ports",
        lazy="joined",
    )

    @property
    def is_expiring_soon(self) -> bool:
        if not self.expires_on:
            return False
        return (
            self.expires_on
            - timedelta(days=settings.ACCESS_DURATION_EXPIRING_SOON_DAYS)
            < datetime.now()
        )

    def to_event(self) -> InputPortEvent:
        return InputPortEvent(
            id=self.id,
            consuming_abstract_data_product_id=self.consuming_abstract_data_product_id,
            consuming_abstract_data_product_type=self.consuming_abstract_data_product.abstract_data_product_type,
        )
