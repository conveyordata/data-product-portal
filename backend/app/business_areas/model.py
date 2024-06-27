import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from app.database.database import Base
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.datasets.model import Dataset
    from app.data_products.model import DataProduct


class BusinessArea(Base, BaseORM):
    __tablename__ = "business_areas"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(String)
    datasets: Mapped[list["Dataset"]] = relationship(lazy="noload")
    data_products: Mapped[list["DataProduct"]] = relationship(lazy="noload")
