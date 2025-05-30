from typing import Sequence
from uuid import UUID

from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.tags.model import Tag as TagModel
from app.tags.model import ensure_tag_exists
from app.tags.schema_request import TagCreate, TagUpdate
from app.tags.schema_response import TagsGet


class TagService:
    def __init__(self, db: Session):
        self.db = db

    def get_tags(self) -> Sequence[TagsGet]:
        return self.db.scalars(select(TagModel).order_by(asc(TagModel.value))).all()

    def create_tag(self, tag: TagCreate) -> dict[str, UUID]:
        tag = TagModel(**tag.parse_pydantic_schema())
        self.db.add(tag)
        self.db.commit()

        return {"id": tag.id}

    def update_tag(self, id: UUID, tag: TagUpdate) -> dict[str, UUID]:
        current_tag = ensure_tag_exists(id, self.db)
        updated_tag = tag.model_dump(exclude_unset=True)

        for attr, value in updated_tag.items():
            setattr(current_tag, attr, value)

        self.db.commit()
        return {"id": id}

    def remove_tag(self, id: UUID) -> None:
        tag = self.db.get(TagModel, id)
        self.db.delete(tag)
        self.db.commit()
