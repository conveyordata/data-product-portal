from uuid import UUID

from app.shared.schema import ORMModel


class TagCreate(ORMModel):
    value: str


class Tag(TagCreate):
    id: UUID
