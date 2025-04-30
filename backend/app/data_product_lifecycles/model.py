import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from app.database.database import Base
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.data_products.model import DataProduct
    from app.datasets.model import Dataset


class DataProductLifecycle(Base, BaseORM):
    __tablename__ = "data_product_lifecycles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    value = Column(Integer)
    color = Column(String)
    is_default = Column(Boolean, server_default="false")

    # Relationships
    data_products: Mapped[list["DataProduct"]] = relationship(
        lazy="raise", back_populates="lifecycle", cascade="all, delete-orphan"
    )
    datasets: Mapped[list["Dataset"]] = relationship(
        lazy="raise", back_populates="lifecycle", cascade="all, delete-orphan"
    )
