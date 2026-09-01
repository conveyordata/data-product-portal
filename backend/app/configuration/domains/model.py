import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    func,
    literal_column,
    select,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, deferred, relationship

from app.database.database import Base, ensure_exists
from app.shared.model import BaseORM, utcnow

if TYPE_CHECKING:
    from app.abstract_data_product.model import AbstractDataProduct
    from app.configuration.environments.model import Environment


domain_environment_table = Table(
    "domain_environments",
    Base.metadata,
    Column("domain_id", ForeignKey("domains.id")),
    Column("environment_id", ForeignKey("environments.id")),
    Column("created_on", DateTime(timezone=False), server_default=utcnow()),
    Column("updated_on", DateTime(timezone=False), onupdate=utcnow()),
)


class Domain(Base, BaseORM):
    __tablename__ = "domains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(String)

    abstract_data_products: Mapped[list["AbstractDataProduct"]] = relationship(
        "AbstractDataProduct", lazy="raise"
    )
    environments: Mapped[list["Environment"]] = relationship(
        secondary=domain_environment_table, lazy="raise"
    )

    abstract_data_product_count = deferred(
        select(func.count(literal_column("id")))
        .select_from(text("abstract_data_products"))
        .scalar_subquery(),
        raiseload=True,
    )


def ensure_domain_exists(data_product_type_id: UUID, db: Session, **kwargs) -> Domain:
    return ensure_exists(data_product_type_id, db, Domain, **kwargs)
