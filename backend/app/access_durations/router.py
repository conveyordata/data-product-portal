from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.abstract_data_product.type import AbstractDataProductType
from app.access_durations.schema_request import AccessDurationUpdate
from app.access_durations.schema_response import (
    AccessDuration,
    TimeBoundAccessEnabledResponse,
)
from app.access_durations.service import AccessDurationService
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.database import get_db_session
from app.settings import settings

router = APIRouter(tags=["Access Durations"], prefix="/v2/access_durations")


@router.get("/enabled", response_model=TimeBoundAccessEnabledResponse)
def is_time_bound_access_enabled():
    return TimeBoundAccessEnabledResponse(enabled=settings.TIME_BOUND_ACCESS_ENABLED)


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
    return AccessDurationService(db).get_access_durations()


@router.put(
    "/{abstract_data_product_type}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def update_access_duration(
    abstract_data_product_type: AbstractDataProductType,
    update: AccessDurationUpdate,
    db: Session = Depends(get_db_session),
) -> list[AccessDuration]:
    return AccessDurationService(db).upsert_access_duration(
        abstract_data_product_type, update
    )
