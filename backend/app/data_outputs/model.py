import uuid

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from app.data_outputs.data_output_types import DataOutputTypes
from app.data_products.model import DataProduct
from app.database.database import Base
from app.shared.model import BaseORM


class DataOutput(Base, BaseORM):
    __tablename__ = "data_outputs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    owner_id: Mapped[UUID] = Column(ForeignKey("data_products.id"))
    owner: Mapped["DataProduct"] = relationship(back_populates="data_outputs")
    configuration_type: DataOutputTypes = Column(Enum(DataOutputTypes))
    configuration = Column(String)
