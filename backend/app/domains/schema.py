from uuid import UUID

from pydantic import Field

from app.domains.schema_create import DomainCreate


class Domain(DomainCreate):
    id: UUID = Field(..., description="Unique identifier for the domain")
