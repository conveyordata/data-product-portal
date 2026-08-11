from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.configuration.platform_service_configurations.schema import (
    GetAllPlatformServiceConfigurationsResponse,
    PlatformServiceConfiguration,
)
from app.configuration.platform_service_configurations.service import (
    PlatformServiceConfigurationService,
)
from app.configuration.platforms.platform_services.service import PlatformServiceService
from app.configuration.platforms.schema_response import (
    GetAllPlatformsResponse,
)

from .platform_services.schema_response import GetPlatformServicesResponse
from .service import PlatformService as PlatformsService

router = APIRouter(
    tags=["Configuration - Platforms"], prefix="/v2/configuration/platforms"
)


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
    id: UUID,
    service_id: UUID,
    platform_service_configuration_service: PlatformServiceConfigurationService = Depends(
        PlatformServiceConfigurationService
    ),
) -> PlatformServiceConfiguration:
    if not (
        service_config
        := platform_service_configuration_service.get_platform_service_configuration(
            id, service_id
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform service configuration not found",
        )
    return service_config


@router.get("/configs/{config_id}")
def get_single_platform_service_configuration(
    config_id: UUID,
    platform_service_configuration_service: PlatformServiceConfigurationService = Depends(
        PlatformServiceConfigurationService
    ),
) -> PlatformServiceConfiguration:
    return platform_service_configuration_service.get_single_platform_service_configuration(
        config_id
    )


@router.get("/configs")
def get_all_platform_service_configurations(
    platform_service_configuration_service: PlatformServiceConfigurationService = Depends(
        PlatformServiceConfigurationService
    ),
) -> GetAllPlatformServiceConfigurationsResponse:
    return GetAllPlatformServiceConfigurationsResponse(
        platform_service_configurations=platform_service_configuration_service.get_all_platform_service_configurations()
    )


@router.get("")
def get_all_platforms(
    platform_service: PlatformsService = Depends(PlatformsService),
) -> GetAllPlatformsResponse:
    return GetAllPlatformsResponse(platforms=platform_service.get_all_platforms())


@router.get("/{id}/services")
def get_platform_services(
    id: UUID,
    platform_service_service: PlatformServiceService = Depends(PlatformServiceService),
) -> GetPlatformServicesResponse:
    return GetPlatformServicesResponse(
        platform_services=platform_service_service.get_platform_services(id)
    )
