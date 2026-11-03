import uuid

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.database.database import Base
from app.shared.model import BaseORM


class Environment(Base, BaseORM):
    __tablename__ = "environments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, primary_key=True)
    acronym = Column(String, unique=True)
    context = Column(String)
    is_default = Column(Boolean, default=False)
    is_global = Column(Boolean, default=True, nullable=False)
    position = Column(Integer, nullable=True)


ENVIRONMENT_DISPLAY_ORDER = (Environment.position.asc().nulls_last(), Environment.name)
