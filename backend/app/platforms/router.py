from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.dependencies import only_for_admin

from .schemas import (
    Identifiers,
    PlatformSchema,
    PlatformServiceConfigSchema,
    PlatformServiceSchema,
)
from .service import PlatformsService

router = APIRouter(prefix="/platforms", tags=["platforms"])


@router.get("")
def get_all_platforms(
    db: Session = Depends(get_db_session),
) -> Sequence[PlatformSchema]:
    return PlatformsService(db).get_all_platforms()


@router.get("/{platform_id}/services")
def get_platform_services(
    platform_id: UUID, db: Session = Depends(get_db_session)
) -> Sequence[PlatformServiceSchema]:
    return PlatformsService(db).get_platform_services(platform_id)


@router.get(
    "/{platform_id}/services/{service_id}",
    dependencies=[Depends(only_for_admin)],
    description="Get Platform Service config",
    responses={
        404: {
            "description": "Platform service configuration not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Platform service configuration not found"}
                }
            },
        }
    },
)
def get_platform_service_config(
    platform_id: UUID, service_id: UUID, db: Session = Depends(get_db_session)
) -> PlatformServiceConfigSchema:
    if not (config := PlatformsService(db).get_service_config(platform_id, service_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform service configuration not found",
        )
    return config


@router.post(
    "/{platform_id}/services/{service_id}",
    dependencies=[Depends(only_for_admin)],
    status_code=status.HTTP_201_CREATED,
)
def create_platform_service_config(
    platform_id: UUID,
    service_id: UUID,
    config: Identifiers,
    db: Session = Depends(get_db_session),
):
    PlatformsService(db).create_service_config(
        platform_id, service_id, config.model_dump_json()
    )


@router.get("/configs")
def get_platforms_configurations(
    db: Session = Depends(get_db_session),
) -> Sequence[PlatformServiceConfigSchema]:
    return PlatformsService(db).get_platforms_configs()


@router.get("/configs/{config_id}", dependencies=[Depends(only_for_admin)])
def get_platform_service_configuration(
    config_id: UUID, db: Session = Depends(get_db_session)
) -> PlatformServiceConfigSchema:
    return PlatformsService(db).get_platform_service_config(config_id)
