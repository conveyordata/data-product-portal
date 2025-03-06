from uuid import UUID

from app.domains.schema_create import DomainCreate


class Domain(DomainCreate):
    id: UUID
