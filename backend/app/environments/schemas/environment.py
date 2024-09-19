from uuid import UUID

from app.shared.schema import ORMModel


class Environment(ORMModel):
    name: str
    context: str
    is_default: bool = False


class GetEnvironment(Environment):
    id: UUID
