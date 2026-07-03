from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.abstract_data_product.type import AbstractDataProductType
from app.access_durations.schema_response import AccessDuration
from app.access_durations.service import AccessDurationService
from app.database.database import get_db_session

router = APIRouter(tags=["Access Durations"], prefix="/v2/access_durations")


@router.get("/{abstract_data_product_type}/default", response_model=AccessDuration)
def get_default_access_duration(
    abstract_data_product_type: AbstractDataProductType,
    db: Session = Depends(get_db_session),
):
    access_duration = AccessDurationService(db).get_default_access_duration(
        abstract_data_product_type
    )
    if access_duration is None:
        raise HTTPException(
            status_code=404,
            detail="No default access duration found for the given abstract data product type.",
        )
    return access_duration


@router.get("", response_model=list[AccessDuration])
def get_all_access_durations(db: Session = Depends(get_db_session)):
    access_durations = AccessDurationService(db).get_access_durations()
    return access_durations
