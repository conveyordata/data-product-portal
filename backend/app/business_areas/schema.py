from uuid import UUID

from app.business_areas.schema_create import BusinessAreaCreate


class BusinessArea(BusinessAreaCreate):
    id: UUID
