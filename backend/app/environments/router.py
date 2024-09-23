from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.dependencies import only_for_admin
from app.environment_platform_configurations.schema import (
    EnvironmentPlatformConfiguration,
)
from app.environment_platform_service_configurations.schema import (
    EnvironmentPlatformServiceConfiguration,
)
from app.environments.schema import Environment, EnvironmentCreate
from app.environments.service import EnvironmentService

router = APIRouter(prefix="/envs", tags=["environments"])


@router.get("")
def get_environments(db: Session = Depends(get_db_session)) -> Sequence[Environment]:
    return EnvironmentService(db).get_environments()


@router.post("", dependencies=[Depends(only_for_admin)])
def create_environment(
    environment: EnvironmentCreate, db: Session = Depends(get_db_session)
):
    EnvironmentService(db).create_environment(environment)


@router.get("/{environment_id}/configs", dependencies=[Depends(only_for_admin)])
def get_environment_configs(
    environment_id: UUID,
    db: Session = Depends(get_db_session),
) -> Sequence[EnvironmentPlatformServiceConfiguration]:
    return EnvironmentService(db).get_environment_configs(environment_id)


@router.get(
    "/{environment_id}/platforms/{platform_id}/services/{service_id}/config",
    dependencies=[Depends(only_for_admin)],
)
def get_environment_platform_service_config(
    environment_id: UUID,
    platform_id: UUID,
    service_id: UUID,
    db: Session = Depends(get_db_session),
) -> EnvironmentPlatformServiceConfiguration:
    return EnvironmentService(db).get_environment_platform_service_config(
        environment_id, platform_id, service_id
    )


@router.get(
    "/{environment_id}/platforms/{platform_id}/config",
    dependencies=[Depends(only_for_admin)],
)
def get_environment_platform_config(
    environment_id: UUID,
    platform_id: UUID,
    db: Session = Depends(get_db_session),
) -> EnvironmentPlatformConfiguration:
    return EnvironmentService(db).get_environment_platform_config(
        environment_id, platform_id
    )
