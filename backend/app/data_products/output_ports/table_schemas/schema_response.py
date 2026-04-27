from uuid import UUID

from app.configuration.tags.schema import Tag
from app.shared.schema import ORMModel


class ColumnResponse(ORMModel):
    id: UUID
    name: str
    description: str | None = None
    data_type: str | None = None
    tags: list[Tag]


class TableSchemaResponse(ORMModel):
    id: UUID
    output_port_id: UUID
    name: str
    description: str | None = None
    tags: list[Tag]
    columns: list[ColumnResponse]
