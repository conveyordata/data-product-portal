from typing import TYPE_CHECKING, Sequence

from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.authorization.role_assignments.enums import DecisionStatus
from app.core.webhooks.events import OutputPortTechnicalAssetLinkEvent, V2Event
from app.database.database import Base
from app.database.event_mixin import EventTrackedMixin
from app.settings import settings

if TYPE_CHECKING:
    from app.data_products.output_ports.model import Dataset
    from app.data_products.technical_assets.model import TechnicalAsset
    from app.users.model import User

import uuid

from app.shared.model import BaseORM, utcnow


class DataOutputDatasetAssociation(Base, BaseORM, EventTrackedMixin):
    __tablename__ = "data_outputs_datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status: Mapped[DecisionStatus] = mapped_column(
        Enum(DecisionStatus),
        default=DecisionStatus.PENDING,
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
    data_output: Mapped["TechnicalAsset"] = relationship(
        back_populates="dataset_links",
        order_by="TechnicalAsset.name",
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

    def generate_extra_events(self, connection) -> Sequence[V2Event]:
        if settings.WEBHOOK_V2_TECHNICAL_ASSET_OUTPUT_PORT_LINKS_TRIGGER_INPUT_PORT_EVENTS:
            from sqlalchemy.orm import object_session

            from app.abstract_data_product.input_ports.model import InputPort

            db = object_session(self)
            if db is None:
                return []
            input_ports = (
                db.query(InputPort)
                .filter(InputPort.dataset_id == self.dataset_id)
                .all()
            )
            return [ip.to_event() for ip in input_ports]
        return []

    def to_event(self) -> OutputPortTechnicalAssetLinkEvent:
        return OutputPortTechnicalAssetLinkEvent(
            id=self.id,
            data_product_id=self.dataset.data_product_id
            if self.data_output is None
            else self.data_output.owner_id,
            output_port_id=self.dataset_id,
            technical_asset_id=self.data_output_id,
        )
