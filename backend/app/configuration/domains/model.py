import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.configuration.domains.status import DomainStatus
from app.core.webhooks.events import DomainEvent
from app.database.database import Base, ensure_exists
from app.database.event_mixin import EventTrackedMixin
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.abstract_data_product.model import AbstractDataProduct


class Domain(Base, BaseORM, EventTrackedMixin):
    __tablename__ = "domains"
    __table_args__ = (UniqueConstraint("namespace", name="uq_domains_namespace"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    namespace = Column(String, nullable=False)
    description = Column(String)
    status: Mapped[DomainStatus] = mapped_column(
        SAEnum(
            DomainStatus,
            values_callable=lambda enum: [e.value for e in enum],
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        default=DomainStatus.ACTIVE,
        server_default=DomainStatus.ACTIVE.value,
    )
    finalizers: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list, server_default="{}"
    )

    abstract_data_products: Mapped[list["AbstractDataProduct"]] = relationship(
        "AbstractDataProduct", lazy="raise"
    )

    def to_event(self) -> DomainEvent:
        return DomainEvent(id=self.id)


def ensure_domain_exists(data_product_type_id: UUID, db: Session, **kwargs) -> Domain:
    return ensure_exists(data_product_type_id, db, Domain, **kwargs)
