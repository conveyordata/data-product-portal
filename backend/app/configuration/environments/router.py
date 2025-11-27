from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.configuration.environments.platform_configurations.schema_response import (
    EnvironmentPlatformConfigGet,
)
from app.configuration.environments.platform_configurations.service import (
    EnvironmentPlatformConfigurationService,
)
from app.configuration.environments.platform_service_configurations.schema_response import (
    EnvironmentConfigsGet,
    EnvironmentConfigsGetItem,
)
from app.configuration.environments.platform_service_configurations.service import (
    EnvironmentPlatformServiceConfigurationService,
)
from app.configuration.environments.schema_response import (
    Environment,
    EnvironmentGetItem,
    EnvironmentsGet,
)
from app.configuration.environments.service import EnvironmentService
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.database import get_db_session

router = APIRouter()


@router.get("/{id}")
def get_environment(id: UUID, db: Session = Depends(get_db_session)) -> Environment:
    return EnvironmentService(db).get_environment(id)


@router.get(
    "/configs/{config_id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def get_environment_configs_by_id(
    config_id: UUID,
    db: Session = Depends(get_db_session),
) -> EnvironmentConfigsGetItem:
    return EnvironmentPlatformServiceConfigurationService(
        db
    ).get_environment_platform_service_config_by_id(config_id)


@router.get(
    "/{id}/platforms/{platform_id}/services/{service_id}/config",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def get_environment_platform_service_config(
    id: UUID,
    platform_id: UUID,
    service_id: UUID,
    db: Session = Depends(get_db_session),
) -> EnvironmentConfigsGetItem:
    return EnvironmentPlatformServiceConfigurationService(
        db
    ).get_environment_platform_service_config(id, platform_id, service_id)


@router.get(
    "/{id}/platforms/{platform_id}/config",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def get_environment_platform_config(
    id: UUID,
    platform_id: UUID,
    db: Session = Depends(get_db_session),
) -> EnvironmentPlatformConfigGet:
    return EnvironmentPlatformConfigurationService(db).get_environment_platform_config(
        id, platform_id
    )


_router = router
router = APIRouter(tags=["Configuration - Environments"])
router.include_router(_router, prefix="/envs", deprecated=True)
router.include_router(_router, prefix="/v2/configuration/environments")


@router.get("/envs", deprecated=True)
def get_environments_old(
    db: Session = Depends(get_db_session),
) -> Sequence[EnvironmentGetItem]:
    return get_environments(db).environments


@router.get("/v2/configuration/environments")
def get_environments(db: Session = Depends(get_db_session)) -> EnvironmentsGet:
    return EnvironmentsGet(environments=EnvironmentService(db).get_environments())


@router.get("/envs/{id}/configs", deprecated=True)
def get_environment_configs_old(
    id: UUID,
    db: Session = Depends(get_db_session),
) -> Sequence[EnvironmentConfigsGetItem]:
    return get_environment_configs(id, db).environment_configs


@router.get("/v2/configuration/environments/{id}/configs")
def get_environment_configs(
    id: UUID,
    db: Session = Depends(get_db_session),
) -> EnvironmentConfigsGet:
    return EnvironmentConfigsGet(
        environment_configs=EnvironmentPlatformServiceConfigurationService(
            db
        ).get_environment_platform_service_configs(id)
    )


@router.get(
    "/envs/platforms/{platform_id}/services/{service_id}/config",
    deprecated=True,
)
def get_environment_platform_service_config_for_all_envs_old(
    platform_id: UUID,
    service_id: UUID,
    db: Session = Depends(get_db_session),
) -> Sequence[EnvironmentConfigsGetItem]:
    return get_environment_platform_service_config_for_all_envs(
        platform_id, service_id, db
    ).environment_configs


@router.get(
    "/v2/configuration/environments/platforms/{platform_id}/services/{service_id}/config",
)
def get_environment_platform_service_config_for_all_envs(
    platform_id: UUID,
    service_id: UUID,
    db: Session = Depends(get_db_session),
) -> EnvironmentConfigsGet:
    return EnvironmentPlatformServiceConfigurationService(
        db
    ).get_all_platform_service_configs(platform_id, service_id)
