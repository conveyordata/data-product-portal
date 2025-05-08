import uuid

from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.database.database import Base
from app.shared.model import BaseORM


class Integration(Base, BaseORM):
    __tablename__ = "integrations"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_type = Column(String, primary_key=True)
    url = Column(String)