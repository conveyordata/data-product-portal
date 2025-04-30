from uuid import UUID

from app.shared.schema import ORMModel


class DataProductLifeCycleBasic(ORMModel):
    id: UUID
    name: str
    value: int
    color: str
    is_default: bool
