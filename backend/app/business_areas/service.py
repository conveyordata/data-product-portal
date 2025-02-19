from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.business_areas.model import BusinessArea as BusinessAreaModel
from app.business_areas.model import ensure_business_area_exists
from app.business_areas.schema_create import BusinessAreaCreate, BusinessAreaUpdate
from app.business_areas.schema_get import BusinessAreaGet, BusinessAreasGet


class BusinessAreaService:
    def get_business_areas(self, db: Session) -> list[BusinessAreasGet]:
        return db.query(BusinessAreaModel).order_by(BusinessAreaModel.name).all()

    def get_business_area(self, id: UUID, db: Session) -> BusinessAreaGet:
        business_area = db.get(BusinessAreaModel, id)

        if not business_area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business area not found",
            )

        return business_area

    def create_business_area(
        self, business_area: BusinessAreaCreate, db: Session
    ) -> dict[str, UUID]:
        business_area = BusinessAreaModel(**business_area.parse_pydantic_schema())
        db.add(business_area)
        db.commit()
        return {"id": business_area.id}

    def update_business_area(
        self, id: UUID, business_area: BusinessAreaUpdate, db: Session
    ) -> dict[str, UUID]:
        current_business_area = db.get(BusinessAreaModel, id)
        updated_business_area = business_area.parse_pydantic_schema()

        for attr, value in updated_business_area.items():
            setattr(current_business_area, attr, value)

        db.commit()
        return {"id": id}

    def remove_business_area(self, id: UUID, db: Session):
        business_area = db.get(BusinessAreaModel, id)

        if business_area.data_products or business_area.datasets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Cannot delete a business area assigned to one or multiple "
                    "data products or datasets"
                ),
            )

        db.delete(business_area)
        db.commit()

    def migrate_business_area(self, from_id: UUID, to_id: UUID, db: Session):
        business_area = ensure_business_area_exists(from_id, db)
        new_business_area = ensure_business_area_exists(to_id, db)

        for dataset in business_area.datasets:
            dataset.business_area_id = new_business_area.id

        for data_product in business_area.data_products:
            data_product.business_area_id = new_business_area.id

        db.commit()
