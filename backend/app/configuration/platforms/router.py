from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.configuration.platforms.platform_services.schema import PlatformService
from app.configuration.platforms.platform_services.service import PlatformServiceService
from app.configuration.platforms.schema_response import (
    GetAllPlatformsResponse,
    Platform,
)
from app.database.database import get_db_session
from app.platform_service_configurations.schema import (
    GetAllPlatformServiceConfigurationsResponse,
    PlatformServiceConfiguration,
)
from app.platform_service_configurations.service import (
    PlatformServiceConfigurationService,
)

from .platform_services.schema_response import GetPlatformServicesResponse
from .service import PlatformService as PlatformsService

router = APIRouter(tags=["Configuration - Platforms"])


@router.get(
    "/{id}/services/{service_id}",
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
    id: UUID, service_id: UUID, db: Session = Depends(get_db_session)
) -> PlatformServiceConfiguration:
    if not (
        service_config := PlatformServiceConfigurationService(
            db
        ).get_platform_service_configuration(id, service_id)
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform service configuration not found",
        )
    return service_config


@router.get("/configs/{config_id}")
def get_single_platform_service_configuration(
    config_id: UUID,
    db: Session = Depends(get_db_session),
) -> PlatformServiceConfiguration:
    return PlatformServiceConfigurationService(
        db
    ).get_single_platform_service_configuration(config_id)


_router = router
router = APIRouter()
router.include_router(_router, prefix="/platforms", deprecated=True)
router.include_router(_router, prefix="/v2/configuration/platforms")


@router.get("/platforms/configs", deprecated=True)
def get_all_platform_service_configurations_old(
    db: Session = Depends(get_db_session),
) -> Sequence[PlatformServiceConfiguration]:
    return get_all_platform_service_configurations(db).platform_service_configurations


@router.get("/v2/configuration/platforms/configs")
def get_all_platform_service_configurations(
    db: Session = Depends(get_db_session),
) -> GetAllPlatformServiceConfigurationsResponse:
    return GetAllPlatformServiceConfigurationsResponse(
        platform_service_configurations=PlatformServiceConfigurationService(
            db
        ).get_all_platform_service_configurations()
    )


@router.get("/platforms", deprecated=True)
def get_all_platforms_old(
    db: Session = Depends(get_db_session),
) -> Sequence[Platform]:
    return get_all_platforms(db).platforms


@router.get("/v2/configuration/platforms")
def get_all_platforms(
    db: Session = Depends(get_db_session),
) -> GetAllPlatformsResponse:
    return GetAllPlatformsResponse(platforms=PlatformsService(db).get_all_platforms())


@router.get("/platforms/{id}/services", deprecated=True)
def get_platform_services_old(
    id: UUID, db: Session = Depends(get_db_session)
) -> Sequence[PlatformService]:
    return get_platform_services(id, db).platform_services


@router.get("/v2/configuration/platforms/{id}/services")
def get_platform_services(
    id: UUID, db: Session = Depends(get_db_session)
) -> GetPlatformServicesResponse:
    return GetPlatformServicesResponse(
        platform_services=PlatformServiceService(db).get_platform_services(id)
    )
