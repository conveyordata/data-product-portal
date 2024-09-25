from uuid import UUID

from app.shared.schema import ORMModel


class Environment(ORMModel):
    id: UUID
    name: str
    context: str | None = None
    is_default: bool = False
