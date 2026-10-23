from typing import Optional, Sequence
from uuid import UUID

from app.shared.schema import ORMModel


class Tool(ORMModel):
    id: UUID
    name: str
    description: str
    data_product_id: UUID
    platform_key: str
    tool_type: str
    base_values: dict[str, str]


class GetToolsResponse(ORMModel):
    tools: Sequence[Tool]


class CreateToolResponse(ORMModel):
    id: UUID


class EnvironmentPropertyValue(ORMModel):
    id: UUID
    name: str
    acronym: str
    override: Optional[str]
    effective_value: str


class OverridablePropertyConfiguration(ORMModel):
    name: str
    label: str
    allowed_values: list[str]
    default: str
    base_value: str
    environments: list[EnvironmentPropertyValue]


class ToolEnvironmentConfiguration(ORMModel):
    properties: list[OverridablePropertyConfiguration]
