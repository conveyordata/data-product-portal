from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.abstract_data_product.model import AbstractDataProduct, AbstractDataProductType


class Exploration(AbstractDataProduct):
    __tablename__ = "explorations"

    id: Mapped[UUID] = mapped_column(
        "id", ForeignKey("abstract_data_products.id"), primary_key=True
    )
    __mapper_args__ = {
        "polymorphic_identity": AbstractDataProductType.EXPLORATION,
    }
