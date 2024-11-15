from uuid import UUID

from app.data_contracts.column.model import Column as ColumnModel
from app.shared.schema import ORMModel


class ColumnGet(ORMModel):
    id: UUID
    name: str
    description: str
    data_type: str
    checks: str


class ColumnCreate(ORMModel):
    name: str
    description: str
    data_type: str
    checks: str

    class Meta:
        orm_model = ColumnModel
