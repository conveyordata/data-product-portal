import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.configuration.domains.model import Domain
from app.database.database import Base
from app.shared.model import BaseORM


class AbstractDataProduct(Base, BaseORM):
    __tablename__ = "abstract_data_products"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    namespace = Column(String)

    __mapper_args__ = {
        "polymorphic_identity": "abstract_data_products",
        "polymorphic_on": "abstract_data_product_type",
    }
    abstract_data_product_type = Column(String)

    description = Column(String)
    domain_id: Mapped[UUID] = Column(ForeignKey("domains.id"))
    domain: Mapped[Domain] = relationship(back_populates="data_products", lazy="joined")
