import uuid
from typing import TYPE_CHECKING, Optional

from fastapi import HTTPException, status
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Enum, ForeignKey, String, func, select
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import (
    Mapped,
    Session,
    column_property,
    deferred,
    mapped_column,
    relationship,
)

from app.abstract_data_product.input_ports.model import (
    InputPort,
)
from app.access_durations.enums import AccessDurationType
from app.authorization.role_assignments.enums import DecisionStatus
from app.configuration.tags.model import Tag, tag_dataset_table
from app.core.webhooks.events import OutputPortEvent
from app.data_products.output_port_technical_assets_link.model import (
    DataOutputDatasetAssociation,
)
from app.data_products.output_ports.data_quality.model import (  # noqa: TCH001
    DataQualitySummary,
)
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.status import OutputPortStatus
from app.database.database import Base, ensure_exists
from app.database.event_mixin import EventTrackedMixin
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.authorization.role_assignments.output_port.model import (
        DatasetRoleAssignment,
    )
    from app.configuration.data_product_lifecycles.model import DataProductLifecycle
    from app.configuration.data_product_settings.model import DataProductSettingValue
    from app.data_products.model import DataProduct


class OutputPort(Base, BaseORM, EventTrackedMixin):
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    namespace = Column(String)
    name = Column(String)
    description = Column(String)
    about = Column(String)
    access_type = Column(
        Enum(OutputPortAccessType), default=OutputPortAccessType.UNRESTRICTED
    )
    status: OutputPortStatus = Column(
        Enum(OutputPortStatus), default=OutputPortStatus.ACTIVE
    )
    usage = Column(String, nullable=True)
    search_vector = Column(TSVECTOR)
    embeddings = deferred(Column(Vector(384)))

    # Foreign keys
    lifecycle_id: Mapped[UUID] = mapped_column(
        ForeignKey("data_product_lifecycles.id", ondelete="SET NULL")
    )
    data_product_id: Mapped[UUID] = mapped_column(ForeignKey("data_products.id"))

    # Relationships
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
    data_output_links: Mapped[list["DataOutputDatasetAssociation"]] = relationship(
        "DataOutputDatasetAssociation",
        back_populates="output_port",
        order_by="DataOutputDatasetAssociation.status.desc()",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary=tag_dataset_table, back_populates="datasets", lazy="joined"
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
    data_product: Mapped["DataProduct"] = relationship(
        back_populates="datasets", lazy="joined"
    )
    quality_summary: Mapped[Optional[DataQualitySummary]] = relationship(
        foreign_keys=[DataQualitySummary.output_port_id],
        lazy="joined",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @property
    def quality_status(self) -> Optional[str]:
        """Returns the overall_status from the quality_summary if it exists."""
        return self.quality_summary.overall_status if self.quality_summary else None

    @property
    def data_product_name(self) -> str:
        return self.data_product.name

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
            select(func.count(DataOutputDatasetAssociation.id))
            .where(DataOutputDatasetAssociation.output_port_id == id)
            .correlate_except(DataOutputDatasetAssociation)
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


Dataset = OutputPort


def ensure_output_port_exists(
    dataset_id: UUID,
    db: Session,
    data_product_id: Optional[UUID] = None,
    **kwargs,
) -> OutputPort:
    output_port: OutputPort = ensure_exists(dataset_id, db, OutputPort, **kwargs)
    if data_product_id is not None and output_port.data_product_id != data_product_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Required item {dataset_id} does not exist",
        )
    return output_port
