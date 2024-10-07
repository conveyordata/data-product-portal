from uuid import UUID

from sqlalchemy.orm import Session

from app.business_areas.model import BusinessArea as BusinessAreaModel
from app.business_areas.schema import BusinessArea, BusinessAreaCreate


class BusinessAreaService:
    def get_business_areas(self, db: Session) -> list[BusinessArea]:
        return db.query(BusinessAreaModel).order_by(BusinessAreaModel.name).all()

    def create_business_area(
        self, business_area: BusinessAreaCreate, db: Session
    ) -> dict[str, UUID]:
        business_area = BusinessAreaModel(**business_area.parse_pydantic_schema())
        db.add(business_area)
        db.commit()
        return {"id": business_area.id}
