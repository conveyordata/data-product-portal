from uuid import UUID

from app.shared.schema import ORMModel


class Domain(ORMModel):
    id: UUID
    name: str
    description: str
