import json
from uuid import UUID

from pydantic import field_validator

from app.data_contracts.column.model import Column as ColumnModel
from app.shared.schema import ORMModel


class ColumnBase(ORMModel):
    name: str
    description: str
    data_type: str
    checks: list[str]

    class Meta:
        orm_model = ColumnModel

    @field_validator("checks", mode="before")
    @classmethod
    def parse_settings(cls, v: str | list) -> list:
        if isinstance(v, str):
            return json.loads(v)
        return v


class ColumnGet(ColumnBase):
    id: UUID


class ColumnCreate(ColumnBase):
    pass
