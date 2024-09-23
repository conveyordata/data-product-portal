from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.dependencies import only_for_admin
from app.platform_service_configurations.schema import PlatformServiceConfiguration
from app.platforms.schema import Platform

from .service import PlatformsService

router = APIRouter(prefix="/platforms", tags=["platforms"])


@router.get("")
def get_all_platforms(
    db: Session = Depends(get_db_session),
) -> Sequence[Platform]:
    return PlatformsService(db).get_all_platforms()


@router.get("/{platform_id}/services")
def get_platform_services(
    platform_id: UUID, db: Session = Depends(get_db_session)
) -> Sequence[Platform]:
    return PlatformsService(db).get_platform_services(platform_id)


@router.get(
    "/{platform_id}/services/{service_id}",
    dependencies=[Depends(only_for_admin)],
    responses={
        404: {
            "description": "Service configuration not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Service configuration not found"}
                }
            },
        }
    },
)
def get_service_config(
    platform_id: UUID, service_id: UUID, db: Session = Depends(get_db_session)
) -> PlatformServiceConfiguration:
    if not (
        service_config := PlatformsService(db).get_service_config(
            platform_id, service_id
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service configuration not found",
        )
    return PlatformServiceConfiguration(identifiers=service_config)
