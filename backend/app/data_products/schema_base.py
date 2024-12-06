from typing import Optional
from uuid import UUID

from app.shared.schema import ORMModel


class BaseDataProduct(ORMModel):
    name: str
    external_id: str
    description: str
    type_id: UUID
    about: Optional[str] = None
