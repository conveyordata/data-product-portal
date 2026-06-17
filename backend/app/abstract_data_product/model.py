import uuid
from enum import Enum

from sqlalchemy import Column, ForeignKey, String, func, select
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, Session, deferred, mapped_column, relationship

from app.authorization.role_assignments.enums import DecisionStatus
from app.configuration.domains.model import Domain
from app.data_products.output_ports.model import (
    InputPort,
)
from app.data_products.status import DataProductStatus
from app.database.database import Base, ensure_exists
from app.shared.model import BaseORM


class AbstractDataProductType(str, Enum):
    UNKNOWN = "unknown"
    DATA_PRODUCT = "data_products"
    EXPLORATION = "explorations"


class AbstractDataProduct(Base, BaseORM):
    __tablename__ = "abstract_data_products"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    namespace = Column(String)

    __mapper_args__ = {
        "polymorphic_identity": AbstractDataProductType.UNKNOWN,
        "polymorphic_on": "abstract_data_product_type",
    }
    abstract_data_product_type = Column(
        SAEnum(
            AbstractDataProductType,
            values_callable=lambda enum: [e.value for e in enum],
            native_enum=False,  # keep as string/varchar in DB
            validate_strings=True,
        ),
        nullable=False,
    )

    status: Mapped[DataProductStatus] = mapped_column(
        SAEnum(
            DataProductStatus,
            values_callable=lambda enum: [e.value for e in enum],
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        default=DataProductStatus.ACTIVE,
        server_default=DataProductStatus.ACTIVE.value,
    )

    description = Column(String)
    domain_id: Mapped[UUID] = Column(ForeignKey("domains.id"))
    domain: Mapped[Domain] = relationship(
        back_populates="abstract_data_products", lazy="joined"
    )
    input_ports: Mapped[list["InputPort"]] = relationship(
        back_populates="consuming_abstract_data_product",
        cascade="all, delete-orphan",
        order_by="InputPort.status.desc()",
        lazy="raise",
    )
    input_port_count = deferred(
        select(func.count(InputPort.id))
        .where(InputPort.consuming_abstract_data_product_id == id)
        .where(InputPort.status == DecisionStatus.APPROVED)
        .correlate_except(InputPort)
        .scalar_subquery(),
        raiseload=True,
    )
    finalizers: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list, server_default="{}"
    )


def ensure_abstract_data_product_exists(
    id: UUID, db: Session, **kwargs
) -> AbstractDataProduct:
    return ensure_exists(id, db, AbstractDataProduct, **kwargs)
