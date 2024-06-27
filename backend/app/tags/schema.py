from app.shared.schema import ORMModel
from app.tags.model import Tag as TagModel
from uuid import UUID


class TagCreate(ORMModel):
    value: str

    class Meta:
        orm_model = TagModel


class Tag(TagCreate):
    id: UUID
