from uuid import UUID

from app.business_areas.model import BusinessArea as BusinessAreaModel
from app.shared.schema import ORMModel


class BusinessAreaCreate(ORMModel):
    name: str
    description: str

    class Meta:
        orm_model = BusinessAreaModel


class BusinessArea(BusinessAreaCreate):
    id: UUID


class BusinessAreaUpdate(BusinessAreaCreate):
    pass
