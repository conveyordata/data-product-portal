from typing import Optional
from uuid import UUID

from app.shared.schema import ORMModel


class BaseDataProduct(ORMModel):
    name: str
    namespace: str
    description: str
    type_id: UUID
    about: Optional[str] = None
