from uuid import UUID

from app.shared.schema import ORMModel


class TagCreate(ORMModel):
    value: str

    class Config:
        frozen = True


class Tag(TagCreate):
    id: UUID


class TagUpdate(TagCreate):
    pass
