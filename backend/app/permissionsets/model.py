import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.database.database import Base
from app.shared.model import BaseORM


class Permissionset(Base, BaseORM):
    __tablename__ = "permissionsets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_product = Column(String, ForeignKey("data_products.id"))
    environment = Column(String, ForeignKey("environments.id"))
    name = Column(String)
    rolearn = Column(String)
