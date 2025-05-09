from uuid import UUID

from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.tags.model import Tag as TagModel
from app.tags.model import ensure_tag_exists
from app.tags.schema_request import TagCreate, TagUpdate
from app.tags.schema_response import TagsGet


class TagService:
    def get_tags(self, db: Session) -> list[TagsGet]:
        return db.scalars(select(TagModel).order_by(asc(TagModel.value))).all()

    def create_tag(self, tag: TagCreate, db: Session) -> dict[str, UUID]:
        tag = TagModel(**tag.parse_pydantic_schema())
        db.add(tag)
        db.commit()

        return {"id": tag.id}

    def update_tag(self, id: UUID, tag: TagUpdate, db: Session):
        current_tag = ensure_tag_exists(id, db)
        updated_tag = tag.model_dump(exclude_unset=True)

        for attr, value in updated_tag.items():
            setattr(current_tag, attr, value)

        db.commit()
        return {"id": id}

    def remove_tag(self, id: UUID, db: Session):
        tag = db.get(TagModel, id)
        db.delete(tag)
        db.commit()
