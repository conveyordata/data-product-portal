import uuid

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import mapped_column

from app.database.database import Base
from app.shared.model import BaseORM


class Role(Base, BaseORM):
    __tablename__ = "roles"
    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    scope = Column(String)
    description = Column(String)
    permissions = Column(ARRAY(Integer))
