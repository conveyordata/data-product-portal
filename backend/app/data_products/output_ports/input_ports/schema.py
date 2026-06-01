from uuid import UUID

from app.authorization.role_assignments.enums import DecisionStatus
from app.shared.schema import ORMModel


class InputPortBase(ORMModel):
    id: UUID
    justification: str
    status: DecisionStatus
