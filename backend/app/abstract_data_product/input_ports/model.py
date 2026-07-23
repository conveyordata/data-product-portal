import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    UUID,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.abstract_data_product.input_ports.enums import (
    InputPortRequestDecision,
    InputPortStatus,
    RenewalStatus,
)
from app.access_durations.enums import AccessDurationType
from app.core.webhooks.events import InputPortEvent
from app.database.database import Base
from app.database.event_mixin import EventTrackedMixin
from app.shared.model import BaseORM, utcnow

if TYPE_CHECKING:
    from app.abstract_data_product.model import AbstractDataProduct
    from app.data_products.output_ports.model import OutputPort
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

    consuming_abstract_data_product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("abstract_data_products.id")
    )
    output_port_id: Mapped[uuid.UUID] = mapped_column(
        "dataset_id", ForeignKey("datasets.id")
    )

    # Relationships
    output_port: Mapped["OutputPort"] = relationship(
        "OutputPort",
        back_populates="data_product_links",
        order_by="OutputPort.name",
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
    def current_request(self) -> "InputPortRequest":
        if active_grant := self.active_grant:
            return active_grant
        if self.pending_request is not None and not self._has_real_grant:
            return self.pending_request
        if last_settled := self._last_settled_request:
            return last_settled
        return self.latest_request

    @property
    def latest_request(self) -> "InputPortRequest":
        return max(self.requests, key=lambda request: request.created_on)

    @property
    def _has_real_grant(self) -> bool:
        return any(
            request.decision == InputPortRequestDecision.APPROVED
            for request in self.requests
        )

    @property
    def _last_settled_request(self) -> Optional["InputPortRequest"]:
        return next(
            (
                request
                for request in sorted(
                    self.requests, key=lambda request: request.created_on, reverse=True
                )
                if request.decision
                in (InputPortRequestDecision.APPROVED, InputPortRequestDecision.DENIED)
            ),
            None,
        )

    @property
    def active_grant(self) -> Optional["InputPortRequest"]:
        today = date.today()
        return next(
            (
                request
                for request in sorted(
                    self.requests, key=lambda request: request.created_on, reverse=True
                )
                if request.decision == InputPortRequestDecision.APPROVED
                and request.revoked_at is None
                and (request.valid_from is None or request.valid_from <= today)
                and (request.valid_until is None or request.valid_until >= today)
            ),
            None,
        )

    @property
    def renewal_status(self) -> Optional[RenewalStatus]:
        if self.active_grant is None or self.active_grant.id != self.latest_request.id:
            if not self._has_real_grant:
                return None
            match self.latest_request.decision:
                case InputPortRequestDecision.APPROVED:
                    return None
                case InputPortRequestDecision.DENIED:
                    return RenewalStatus.DENIED
                case InputPortRequestDecision.PENDING:
                    return RenewalStatus.PENDING
                case InputPortRequestDecision.CANCELLED:
                    return None
        return None

    @property
    def pending_request(self) -> Optional["InputPortRequest"]:
        return next(
            (
                request
                for request in self.requests
                if request.decision == InputPortRequestDecision.PENDING
            ),
            None,
        )

    def recompute_status(self) -> None:
        if self.active_grant is not None:
            self.status = InputPortStatus.APPROVED
            return
        if self.pending_request is not None and not self._has_real_grant:
            self.status = InputPortStatus.PENDING
            return
        last_settled = self._last_settled_request
        if last_settled is None:
            self.status = InputPortStatus.CANCELLED
            return
        match last_settled.decision:
            case InputPortRequestDecision.APPROVED:
                self.status = (
                    InputPortStatus.REVOKED
                    if last_settled.revoked_at is not None
                    else InputPortStatus.EXPIRED
                )
            case InputPortRequestDecision.DENIED:
                self.status = InputPortStatus.DENIED

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
    decision: Mapped[InputPortRequestDecision] = mapped_column(
        Enum(InputPortRequestDecision, native_enum=False),
        default=InputPortRequestDecision.PENDING,
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
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
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
    revoked_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
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
    revoked_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[revoked_by_id],
        lazy="joined",
    )
