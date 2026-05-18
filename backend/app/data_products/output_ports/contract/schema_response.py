from typing import Any, Optional
from uuid import UUID

from app.shared.schema import ORMModel


class SchemaPropertyResponse(ORMModel):
    id: UUID
    name: str
    business_name: Optional[str] = None
    logical_type: Optional[str] = None
    physical_type: Optional[str] = None
    description: Optional[str] = None
    examples: Optional[list[Any]] = None
    position: int
    properties: list["SchemaPropertyResponse"] = []


SchemaPropertyResponse.model_rebuild()


class SchemaObjectResponse(ORMModel):
    id: UUID
    name: str
    logical_type: Optional[str] = None
    physical_type: Optional[str] = None
    physical_name: Optional[str] = None
    description: Optional[str] = None
    position: int
    properties: list[SchemaPropertyResponse] = []


class OutputPortSchemaResponse(ORMModel):
    output_port_id: UUID
    schema_objects: list[SchemaObjectResponse] = []
