from typing import Sequence
from uuid import UUID

from sqlalchemy import asc, delete, select
from sqlalchemy.orm import Session

from app.configuration.tags.model import Tag as TagModel
from app.configuration.tags.model import (
    ensure_tag_exists,
    tag_data_product_table,
    tag_output_port_table,
    tag_technical_asset_table,
)
from app.configuration.tags.schema_request import TagCreate, TagUpdate
from app.configuration.tags.schema_response import (
    CreateTagResponse,
    TagsGetItem,
    UpdateTagResponse,
)


class TagService:
    def __init__(self, db: Session):
        self.db = db

    def get_tags(self) -> Sequence[TagsGetItem]:
        return self.db.scalars(select(TagModel).order_by(asc(TagModel.value))).all()

    def create_tag(self, tag: TagCreate) -> CreateTagResponse:
        tag = TagModel(**tag.parse_pydantic_schema())
        self.db.add(tag)
        self.db.flush()

        return CreateTagResponse(id=tag.id)

    def update_tag(self, id: UUID, tag: TagUpdate) -> UpdateTagResponse:
        current_tag = ensure_tag_exists(id, self.db)
        updated_tag = tag.model_dump(exclude_unset=True)

        for attr, value in updated_tag.items():
            setattr(current_tag, attr, value)

        self.db.flush()
        return UpdateTagResponse(id=id)

    def remove_tag(self, id: UUID) -> None:
        # The visibility filters hide some tagged rows from the ORM's cascade.
        for table in (
            tag_data_product_table,
            tag_output_port_table,
            tag_technical_asset_table,
        ):
            self.db.execute(delete(table).where(table.c.tag_id == id))
        tag = self.db.get(TagModel, id)
        self.db.delete(tag)
        self.db.flush()
