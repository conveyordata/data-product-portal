from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.business_areas.schema import BusinessArea, BusinessAreaCreate
from app.business_areas.service import BusinessAreaService
from app.database.database import get_db_session

router = APIRouter(prefix="/business_areas", tags=["business areas"])


@router.get("")
def get_business_areas(db: Session = Depends(get_db_session)) -> list[BusinessArea]:
    return BusinessAreaService().get_business_areas(db)


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
