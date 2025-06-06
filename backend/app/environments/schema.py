from uuid import UUID

from app.shared.schema import ORMModel


class Environment(ORMModel):
    id: UUID
    name: str
    acronym: str
    context: str
    is_default: bool = False
