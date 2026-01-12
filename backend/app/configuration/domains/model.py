import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, relationship

from app.database.database import Base, ensure_exists
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.data_products.model import DataProduct


class Domain(Base, BaseORM):
    __tablename__ = "domains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(String)

    data_products: Mapped[list["DataProduct"]] = relationship(lazy="raise")

    @property
    def data_product_count(self) -> int:
        return len(self.data_products)


def ensure_domain_exists(data_product_type_id: UUID, db: Session, **kwargs) -> Domain:
    return ensure_exists(data_product_type_id, db, Domain, **kwargs)
