from typing import Optional
from uuid import UUID

from app.shared.schema import ORMModel
from app.tags.schema import TagCreate


class BaseDataProduct(ORMModel):
    name: str
    external_id: str
    description: str
    tags: list[TagCreate]
    type_id: UUID
    about: Optional[str] = None
