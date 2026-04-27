from uuid import UUID

from app.shared.schema import ORMModel


class ColumnRequest(ORMModel):
    name: str
    description: str | None = None
    data_type: str | None = None
    tag_ids: list[UUID] = []


class TableSchemaRequest(ORMModel):
    name: str
    description: str | None = None
    tag_ids: list[UUID] = []
    columns: list[ColumnRequest] = []
