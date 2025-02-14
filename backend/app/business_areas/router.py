from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.business_areas.schema_create import BusinessAreaCreate, BusinessAreaUpdate
from app.business_areas.schema_get import BusinessAreaGet, BusinessAreasGet
from app.business_areas.service import BusinessAreaService
from app.database.database import get_db_session

router = APIRouter(prefix="/business_areas", tags=["business areas"])


@router.get("")
def get_business_areas(db: Session = Depends(get_db_session)) -> list[BusinessAreasGet]:
    return BusinessAreaService().get_business_areas(db)


@router.get("/{id}")
def get_business_area(
    id: UUID, db: Session = Depends(get_db_session)
) -> BusinessAreaGet:
    return BusinessAreaService().get_business_area(id, db)


@router.post(
    "",
    responses={
        200: {
            "description": "Business area successfully created",
            "content": {
                "application/json": {
                    "example": {"id": "random id of the new business area"}
                }
            },
        },
    },
)
def create_business_area(
    business_area: BusinessAreaCreate, db: Session = Depends(get_db_session)
) -> dict[str, UUID]:
    return BusinessAreaService().create_business_area(business_area, db)


@router.put("/{id}")
def update_business_area(
    id: UUID, business_area: BusinessAreaUpdate, db: Session = Depends(get_db_session)
):
    return BusinessAreaService().update_business_area(id, business_area, db)


@router.delete("/{id}")
def remove_business_area(id: UUID, db: Session = Depends(get_db_session)):
    return BusinessAreaService().remove_business_area(id, db)


@router.put("/migrate/{from_id}/{to_id}")
def migrate_business_area(
    from_id: UUID, to_id: UUID, db: Session = Depends(get_db_session)
):
    return BusinessAreaService().migrate_business_area(from_id, to_id, db)
