from app.business_areas.model import BusinessArea as BusinessAreaModel
from app.shared.schema import ORMModel


class BusinessAreaCreate(ORMModel):
    name: str
    description: str

    class Meta:
        orm_model = BusinessAreaModel


class BusinessAreaUpdate(BusinessAreaCreate):
    pass
