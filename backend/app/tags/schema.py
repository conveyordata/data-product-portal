from uuid import UUID

from pydantic import Field

from app.shared.schema import ORMModel


class TagCreate(ORMModel):
    value: str = Field(..., description="Value of the tag")

    class Config:
        frozen = True


class Tag(TagCreate):
    id: UUID = Field(..., description="Unique identifier for the tag")


class TagUpdate(TagCreate):
    pass
