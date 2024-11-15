from uuid import UUID

from app.data_contracts.service_level_objective.model import (
    ServiceLevelObjective as ServiceLevelObjectiveModel,
)
from app.shared.schema import ORMModel


class ServiceLevelObjectiveGet(ORMModel):
    id: UUID
    type: str
    value: str
    severity: str


class ServiceLevelObjectiveCreate(ORMModel):
    type: str
    value: str
    severity: str

    class Meta:
        orm_model = ServiceLevelObjectiveModel
