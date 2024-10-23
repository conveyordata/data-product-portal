import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from app.data_product_types.enums import DataProductIconKey
from app.database.database import Base
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.data_products.model import DataProduct


class DataProductType(Base, BaseORM):
    __tablename__ = "data_product_types"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(String)
    icon_key = Column(Enum(DataProductIconKey), default=DataProductIconKey.DEFAULT)
    data_products: Mapped[list["DataProduct"]] = relationship(lazy="noload")
