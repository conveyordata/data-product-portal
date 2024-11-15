from uuid import UUID

from app.data_contracts.column.schema import ColumnCreate, ColumnGet
from app.data_contracts.service_level_objective.schema import (
    ServiceLevelObjectiveCreate,
    ServiceLevelObjectiveGet,
)
from app.shared.schema import ORMModel


class DataContractGet(ORMModel):
    id: UUID
    table: str
    description: str
    checks: str
    columns: list[ColumnGet]
    service_level_objectives: list[ServiceLevelObjectiveGet]


class DataContractCreate(ORMModel):
    data_output_id: UUID
    table: str
    description: str
    checks: str
    columns: list[ColumnCreate]
    service_level_objectives: list[ServiceLevelObjectiveCreate]
