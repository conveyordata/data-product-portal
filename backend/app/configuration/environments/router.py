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
    EnvironmentsGet,
)
from app.configuration.environments.service import EnvironmentService
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.database import get_db_session

router = APIRouter(
    tags=["Configuration - Environments"], prefix="/v2/configuration/environments"
)


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


@router.get("")
def get_environments(db: Session = Depends(get_db_session)) -> EnvironmentsGet:
    return EnvironmentsGet(environments=EnvironmentService(db).get_environments())


@router.get("/{id}/configs")
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
    "/platforms/{platform_id}/services/{service_id}/config",
)
def get_environment_platform_service_config_for_all_envs(
    platform_id: UUID,
    service_id: UUID,
    db: Session = Depends(get_db_session),
) -> EnvironmentConfigsGet:
    return EnvironmentPlatformServiceConfigurationService(
        db
    ).get_all_platform_service_configs(platform_id, service_id)
