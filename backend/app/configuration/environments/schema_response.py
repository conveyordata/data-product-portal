from typing import Sequence
from uuid import UUID

from app.shared.schema import ORMModel


class Environment(ORMModel):
    id: UUID
    name: str
    acronym: str
    context: str
    is_default: bool = False
    is_global: bool = True


class EnvironmentGetItem(Environment):
    pass


class EnvironmentsGet(ORMModel):
    environments: Sequence[EnvironmentGetItem]
