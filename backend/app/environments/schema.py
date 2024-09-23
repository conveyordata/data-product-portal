from uuid import UUID

from app.shared.schema import ORMModel


class EnvironmentCreate(ORMModel):
    name: str
    context: str
    is_default: bool = False


class Environment(EnvironmentCreate):
    id: UUID
