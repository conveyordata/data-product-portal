import uuid
from typing import TYPE_CHECKING, Optional

from fastapi import HTTPException, status
from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    UUID,
    Column,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    func,
    select,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import (
    Mapped,
    Session,
    column_property,
    deferred,
    foreign,
    mapped_column,
    relationship,
)

from app.abstract_data_product.input_ports.model import (
    InputPort,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.model import (  # noqa: TC001
    DatasetRoleAssignment,
)
from app.configuration.access_durations.enums import AccessDurationType
from app.configuration.access_modes.model import AccessMode
from app.configuration.output_port_access_types.model import (
    OutputPortAccessType,
)
from app.configuration.tags.model import Tag, tag_output_port_table
from app.core.webhooks.events import OutputPortEvent
from app.data_products.output_port_technical_assets_link.model import (
    TechnicalAssetOutputPortAssociation,
)
from app.data_products.output_ports.data_quality.model import (  # noqa: TCH001
    DataQualitySummary,
    latest_data_quality_summary,
)
from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.data_products.output_ports.status import OutputPortStatus
from app.data_products.technical_assets.model import TechnicalAssetAccessMode
from app.database.database import (
    Base,
    ensure_exists,
)
from app.database.event_mixin import EventTrackedMixin
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.configuration.data_product_lifecycles.model import DataProductLifecycle
    from app.configuration.data_product_settings.model import DataProductSettingValue
    from app.data_products.model import (
        DataProduct,
    )


output_port_access_modes = (
    select(
        TechnicalAssetOutputPortAssociation.output_port_id.label("output_port_id"),
        TechnicalAssetAccessMode.access_mode_id.label("access_mode_id"),
    )
    .join(
        TechnicalAssetAccessMode,
        TechnicalAssetOutputPortAssociation.technical_asset_id
        == TechnicalAssetAccessMode.technical_asset_id,
    )
    .distinct()
    .subquery()
)


class OutputPort(Base, BaseORM, EventTrackedMixin):
    __tablename__ = "datasets"
    __table_args__ = (
        # access_function is a copy of access_type.access_function;
        # the database keeps it in sync when an access type is remapped.
        ForeignKeyConstraint(
            ["access_type_id", "access_function"],
            [
                "output_port_access_types.id",
                "output_port_access_types.access_function",
            ],
            name="datasets_access_type_fkey",
            onupdate="CASCADE",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    namespace = Column(String)
    name = Column(String)
    description = Column(String)
    about = Column(String)
    access_function = Column(
        Enum(OutputPortAccessFunction, native_enum=False), nullable=False
    )
    status: OutputPortStatus = Column(
        Enum(OutputPortStatus), default=OutputPortStatus.ACTIVE
    )
    usage = Column(String, nullable=True)
    search_vector = Column(TSVECTOR)
    embeddings = deferred(Column(Vector(384)))

    lifecycle_id: Mapped[UUID] = mapped_column(
        ForeignKey("data_product_lifecycles.id", ondelete="SET NULL")
    )
    data_product_id: Mapped[UUID] = mapped_column(ForeignKey("data_products.id"))
    access_type_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )

    assignments: Mapped[list["DatasetRoleAssignment"]] = relationship(
        back_populates="output_port",
        cascade="all, delete-orphan",
        order_by="DatasetRoleAssignment.decision, DatasetRoleAssignment.requested_on",
        lazy="raise",
    )
    data_product_links: Mapped[list["InputPort"]] = relationship(
        "InputPort",
        back_populates="output_port",
        order_by="InputPort.status.desc()",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    technical_asset_links: Mapped[list["TechnicalAssetOutputPortAssociation"]] = (
        relationship(
            "TechnicalAssetOutputPortAssociation",
            back_populates="output_port",
            order_by="TechnicalAssetOutputPortAssociation.status.desc()",
            cascade="all, delete-orphan",
            lazy="raise",
        )
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary=tag_output_port_table,
        back_populates="output_ports",
        lazy="selectin",
        passive_deletes=True,
    )
    data_product_settings: Mapped[list["DataProductSettingValue"]] = relationship(
        "DataProductSettingValue",
        back_populates="output_port",
        cascade="all, delete-orphan",
        order_by="DataProductSettingValue.output_port_id",
        lazy="raise",
    )
    lifecycle: Mapped["DataProductLifecycle"] = relationship(
        back_populates="datasets", lazy="joined"
    )
    access_type: Mapped[OutputPortAccessType] = relationship(lazy="joined")
    data_product: Mapped["DataProduct"] = relationship(
        back_populates="datasets", lazy="joined"
    )
    quality_summary: Mapped[Optional[DataQualitySummary]] = relationship(
        latest_data_quality_summary,
        primaryjoin=lambda: (
            foreign(latest_data_quality_summary().output_port_id) == OutputPort.id
        ),
        lazy="selectin",
        uselist=False,
        viewonly=True,
    )

    @property
    def quality_status(self) -> Optional[str]:
        return self.quality_summary.overall_status if self.quality_summary else None

    @property
    def data_product_name(self) -> str:
        return self.data_product.name

    access_modes: Mapped[list["AccessMode"]] = relationship(
        AccessMode,
        secondary=output_port_access_modes,
        primaryjoin=id == foreign(output_port_access_modes.c.output_port_id),
        secondaryjoin=AccessMode.id
        == foreign(output_port_access_modes.c.access_mode_id),
        order_by="AccessMode.name",
        viewonly=True,
        lazy="selectin",
    )

    abstract_data_product_count = deferred(
        column_property(
            select(func.count(InputPort.id))
            .where(InputPort.output_port_id == id)
            .where(InputPort.status == DecisionStatus.APPROVED)
            .correlate_except(InputPort)
            .scalar_subquery()
        ),
        raiseload=True,
    )
    technical_assets_count = deferred(
        column_property(
            select(func.count(TechnicalAssetOutputPortAssociation.id))
            .where(TechnicalAssetOutputPortAssociation.output_port_id == id)
            .correlate_except(TechnicalAssetOutputPortAssociation)
            .scalar_subquery()
        ),
        raiseload=True,
    )

    data_product_access_duration_type: Mapped[AccessDurationType] = mapped_column(
        Enum(
            AccessDurationType,
            values_callable=lambda enum: [e.value for e in enum],
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    )

    exploration_access_duration_type: Mapped[AccessDurationType] = mapped_column(
        Enum(
            AccessDurationType,
            values_callable=lambda enum: [e.value for e in enum],
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    )

    def to_event(self) -> OutputPortEvent:
        return OutputPortEvent(
            id=self.id,
            data_product_id=self.data_product_id,
        )


def ensure_output_port_exists(
    output_port_id: UUID,
    db: Session,
    data_product_id: Optional[UUID] = None,
    **kwargs,
) -> OutputPort:
    output_port: OutputPort = ensure_exists(output_port_id, db, OutputPort, **kwargs)
    if data_product_id is not None and output_port.data_product_id != data_product_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Required item {output_port_id} does not exist",
        )
    return output_port
