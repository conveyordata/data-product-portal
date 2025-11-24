from uuid import UUID

from app.shared.schema import ORMModel


class DataProductLifeCycle(ORMModel):
    id: UUID
    name: str
    value: int
    color: str
    is_default: bool
