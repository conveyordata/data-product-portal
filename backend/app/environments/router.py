from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization, DataProductResolver
from app.database.database import get_db_session
from app.environment_platform_configurations.schema import (
    EnvironmentPlatformConfiguration,
)
from app.environment_platform_configurations.service import (
    EnvironmentPlatformConfigurationService,
)
from app.environment_platform_service_configurations.schema import (
    EnvironmentPlatformServiceConfiguration,
)
from app.environment_platform_service_configurations.service import (
    EnvironmentPlatformServiceConfigurationService,
)
from app.environments.schema import Environment
from app.environments.service import EnvironmentService

router = APIRouter(prefix="/envs", tags=["environments"])


@router.get("")
def get_environments(db: Session = Depends(get_db_session)) -> Sequence[Environment]:
    return EnvironmentService(db).get_environments()


@router.get("/{id}")
def get_environment(id: UUID, db: Session = Depends(get_db_session)) -> Environment:
    return EnvironmentService(db).get_environment(id)


@router.get("/{id}/configs")
def get_environment_configs(
    id: UUID,
    db: Session = Depends(get_db_session),
) -> Sequence[EnvironmentPlatformServiceConfiguration]:
    return EnvironmentPlatformServiceConfigurationService(
        db
    ).get_environment_platform_service_configs(id)


@router.get(
    "/configs/{config_id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__UPDATE_CONFIGURATION, DataProductResolver
            )
        ),
    ],
)
def get_environment_configs_by_id(
    config_id: UUID,
    db: Session = Depends(get_db_session),
) -> EnvironmentPlatformServiceConfiguration:
    return EnvironmentPlatformServiceConfigurationService(
        db
    ).get_environment_platform_service_config_by_id(config_id)


@router.get(
    "/{id}/platforms/{platform_id}/services/{service_id}/config",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__UPDATE_CONFIGURATION, DataProductResolver
            )
        ),
    ],
)
def get_environment_platform_service_config(
    id: UUID,
    platform_id: UUID,
    service_id: UUID,
    db: Session = Depends(get_db_session),
) -> EnvironmentPlatformServiceConfiguration:
    return EnvironmentPlatformServiceConfigurationService(
        db
    ).get_environment_platform_service_config(id, platform_id, service_id)


@router.get(
    "/platforms/{platform_id}/services/{service_id}/config",
)
def get_environment_platform_service_config_for_all_envs(
    platform_id: UUID,
    service_id: UUID,
    db: Session = Depends(get_db_session),
) -> Sequence[EnvironmentPlatformServiceConfiguration]:
    return EnvironmentPlatformServiceConfigurationService(
        db
    ).get_all_platform_service_configs(platform_id, service_id)


@router.get(
    "/{id}/platforms/{platform_id}/config",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__UPDATE_CONFIGURATION, DataProductResolver
            )
        ),
    ],
)
def get_environment_platform_config(
    id: UUID,
    platform_id: UUID,
    db: Session = Depends(get_db_session),
) -> EnvironmentPlatformConfiguration:
    return EnvironmentPlatformConfigurationService(db).get_environment_platform_config(
        id, platform_id
    )
