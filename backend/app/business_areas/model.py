import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, relationship

from app.database.database import Base, ensure_exists
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.data_products.model import DataProduct
    from app.datasets.model import Dataset


class BusinessArea(Base, BaseORM):
    __tablename__ = "business_areas"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(String)
    datasets: Mapped[list["Dataset"]] = relationship(lazy="select")
    data_products: Mapped[list["DataProduct"]] = relationship(lazy="select")


def ensure_business_area_exists(
    data_product_type_id: UUID, db: Session
) -> BusinessArea:
    return ensure_exists(data_product_type_id, db, BusinessArea)
