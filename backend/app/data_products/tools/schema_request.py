from uuid import UUID

from app.shared.schema import ORMModel


class CreateToolRequest(ORMModel):
    name: str
    description: str = ""
    platform_key: str
    tool_type: str
    base_values: dict[str, str] = {}


class UpdateToolEnvironmentConfigurationRequest(ORMModel):
    base_values: dict[str, str] = {}
    overrides: dict[UUID, dict[str, str]] = {}
