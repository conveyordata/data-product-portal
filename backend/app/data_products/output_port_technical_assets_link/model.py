from typing import TYPE_CHECKING, Sequence

from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.authorization.role_assignments.enums import DecisionStatus
from app.core.webhooks.events import OutputPortTechnicalAssetLinkEvent, V2Event
from app.database.database import Base
from app.database.event_mixin import EventTrackedMixin
from app.settings import settings

if TYPE_CHECKING:
    from app.data_products.output_ports.model import OutputPort
    from app.data_products.technical_assets.model import TechnicalAsset
    from app.users.model import User

import uuid

from app.shared.model import BaseORM, utcnow


class TechnicalAssetOutputPortAssociation(Base, BaseORM, EventTrackedMixin):
    __tablename__ = "data_outputs_datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status: Mapped[DecisionStatus] = mapped_column(
        Enum(DecisionStatus),
        default=DecisionStatus.PENDING,
    )
    requested_on = Column(DateTime(timezone=False), server_default=utcnow())
    approved_on = Column(DateTime(timezone=False))
    denied_on = Column(DateTime(timezone=False))

    technical_asset_id: Mapped[uuid.UUID] = mapped_column(
        "data_output_id", ForeignKey("data_outputs.id")
    )
    output_port_id: Mapped[uuid.UUID] = mapped_column(
        "dataset_id", ForeignKey("datasets.id")
    )
    requested_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    approved_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    denied_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    technical_asset: Mapped["TechnicalAsset"] = relationship(
        back_populates="output_port_links",
        order_by="TechnicalAsset.name",
        lazy="joined",
    )
    output_port: Mapped["OutputPort"] = relationship(
        back_populates="technical_asset_links",
        order_by="OutputPort.name",
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

    def generate_extra_events(self, connection) -> Sequence[V2Event]:
        if settings.WEBHOOK_V2_TECHNICAL_ASSET_OUTPUT_PORT_LINKS_TRIGGER_INPUT_PORT_EVENTS:
            from sqlalchemy.orm import object_session

            from app.abstract_data_product.input_ports.model import InputPort

            db = object_session(self)
            if db is None:
                return []
            input_ports = (
                db.query(InputPort)
                .filter(InputPort.output_port_id == self.output_port_id)
                .all()
            )
            return [ip.to_event() for ip in input_ports]
        return []

    def to_event(self) -> OutputPortTechnicalAssetLinkEvent:
        return OutputPortTechnicalAssetLinkEvent(
            id=self.id,
            data_product_id=self.output_port.data_product_id
            if self.technical_asset is None
            else self.technical_asset.owner_id,
            output_port_id=self.output_port_id,
            technical_asset_id=self.technical_asset_id,
        )
