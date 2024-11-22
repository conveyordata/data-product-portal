import json
from typing import Optional
from uuid import UUID

from pydantic import field_validator

from app.data_contracts.column.schema import ColumnCreate, ColumnGet
from app.data_contracts.service_level_objective.schema import (
    ServiceLevelObjectiveCreate,
    ServiceLevelObjectiveGet,
)
from app.shared.schema import ORMModel


class DataContractBase(ORMModel):
    table: str
    description: str
    checks: list[str]

    @field_validator("checks", mode="before")
    @classmethod
    def parse_settings(cls, v: str | list) -> list:
        if isinstance(v, str):
            return json.loads(v)
        return v


class DataContractGet(DataContractBase):
    id: UUID
    columns: list[ColumnGet]
    service_level_objectives: list[ServiceLevelObjectiveGet]
    quality_score: Optional[int]


class DataContractCreate(DataContractBase):
    data_output_id: UUID
    columns: list[ColumnCreate]
    service_level_objectives: list[ServiceLevelObjectiveCreate]


class QualityScoreUpdate(ORMModel):
    quality_score: int
