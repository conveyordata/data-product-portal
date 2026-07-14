import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.access_durations.enums import AccessDurationType
from app.authorization.role_assignments.enums import DecisionStatus
from app.core.webhooks.events import InputPortEvent
from app.database.database import Base
from app.database.event_mixin import EventTrackedMixin
from app.shared.model import BaseORM, utcnow

if TYPE_CHECKING:
    from app.abstract_data_product.model import AbstractDataProduct
    from app.data_products.output_ports.model import Dataset
    from app.users.model import User


class InputPort(
    Base,
    BaseORM,
    EventTrackedMixin,
):
    __tablename__ = "input_ports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status: Mapped[InputPortStatus] = mapped_column(
        Enum(InputPortStatus, native_enum=False),
        default=InputPortStatus.PENDING,
    )
    expiry_event_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    consuming_abstract_data_product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("abstract_data_products.id")
    )
    dataset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("datasets.id"))

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
    requests: Mapped[list["InputPortRequest"]] = relationship(
        "InputPortRequest",
        back_populates="input_port",
        order_by="InputPortRequest.requested_on",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise",
    )

    @property
    def _current_request(self) -> "InputPortRequest":
        # TODO: handle here different ordering when renewals are implemented.
        return max(self.requests, key=lambda request: request.requested_on)

    @property
    def justification(self) -> str:
        return self._current_request.justification

    @property
    def decision_note(self) -> Optional[str]:
        return self._current_request.decision_note

    @property
    def requested_on(self) -> datetime:
        return self._current_request.requested_on

    @property
    def requested_by(self) -> "User":
        return self._current_request.requested_by

    @property
    def approved_by(self) -> Optional["User"]:
        request = self._current_request
        return (
            request.decided_by if request.decision == DecisionStatus.APPROVED else None
        )

    @property
    def denied_by(self) -> Optional["User"]:
        request = self._current_request
        return (
            request.decided_by if request.decision == DecisionStatus.DENIED else None
        )

    def to_event(self) -> InputPortEvent:
        return InputPortEvent(
            id=self.id,
            consuming_abstract_data_product_id=self.consuming_abstract_data_product_id,
            consuming_abstract_data_product_type=self.consuming_abstract_data_product.abstract_data_product_type,
        )


class InputPortRequest(
    Base,
    BaseORM,
):
    __tablename__ = "input_port_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    decision: Mapped[DecisionStatus] = mapped_column(
        Enum(DecisionStatus, native_enum=False),
        default=DecisionStatus.PENDING,
    )
    justification: Mapped[str] = mapped_column(Text)
    decision_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    access_duration_type: Mapped[AccessDurationType] = mapped_column(
        Enum(AccessDurationType, native_enum=False),
        default=AccessDurationType.PERMANENT,
    )
    requested_duration_days: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    requested_on = Column(DateTime(timezone=False), server_default=utcnow())
    decided_on: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    valid_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    valid_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    input_port_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("input_ports.id", ondelete="CASCADE")
    )
    requested_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    decided_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    input_port: Mapped["InputPort"] = relationship(
        "InputPort",
        back_populates="requests",
    )
    requested_by: Mapped["User"] = relationship(
        "User",
        foreign_keys=[requested_by_id],
        lazy="joined",
    )
    decided_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[decided_by_id],
        lazy="joined",
    )