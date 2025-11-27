from typing import Sequence
from uuid import UUID

from app.shared.schema import ORMModel


class BaseTagGet(ORMModel):
    id: UUID
    value: str


class TagGet(BaseTagGet):
    pass


class TagsGetItem(BaseTagGet):
    pass


class TagsGet(ORMModel):
    tags: Sequence[TagsGetItem]


class CreateTagResponse(ORMModel):
    id: UUID


class UpdateTagResponse(ORMModel):
    id: UUID
