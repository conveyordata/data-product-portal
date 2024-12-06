import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session

from app.database.database import Base, ensure_exists
from app.shared.model import BaseORM
from app.tags.schema import Tag as TagSchema


def ensure_tag_exists(tag_id: UUID, db: Session) -> TagSchema:
    return ensure_exists(tag_id, db, Tag)


class Tag(Base, BaseORM):
    __tablename__ = "tags"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    value = Column(String)
