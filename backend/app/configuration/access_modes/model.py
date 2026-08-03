import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.database.database import Base
from app.shared.model import BaseORM


class AccessMode(Base, BaseORM):
    __tablename__ = "access_modes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(String)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AccessMode):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash((AccessMode, self.id))
