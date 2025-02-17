from uuid import UUID

from sqlalchemy import asc
from sqlalchemy.orm import Session

from app.tags.model import Tag as TagModel
from app.tags.schema import Tag as TagGet
from app.tags.schema import TagCreate


class TagService:
    def get_tags(self, db: Session) -> list[TagGet]:
        return db.query(TagModel).order_by(asc(TagModel.value)).all()

    def create_tag(self, tag: TagCreate, db: Session) -> dict[str, UUID]:
        tag = TagModel(**tag.parse_pydantic_schema())
        db.add(tag)
        db.commit()

        return {"id": tag.id}

    def remove_tag(self, id: UUID, db: Session):
        tag = db.get(TagModel, id)
        db.delete(tag)
        db.commit()
