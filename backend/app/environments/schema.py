from uuid import UUID

from pydantic import Field

from app.shared.schema import ORMModel


class Environment(ORMModel):
    id: UUID = Field(..., description="Unique identifier for the environment")
    name: str = Field(..., description="Name of the environment")
    context: str = Field(..., description="Context of the environment")
    is_default: bool = Field(
        False, description="Indicates if this is the default environment"
    )
