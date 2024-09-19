from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.dependencies import only_for_admin
from app.environments.schemas import (
    Environment,
    EnvPlatformConfig,
    EnvPlatformServiceConfig,
    GetEnvironment,
)
from app.environments.service import EnvironmentService

router = APIRouter(prefix="/envs", tags=["environments"])


@router.get("")
def get_environments(db: Session = Depends(get_db_session)) -> Sequence[GetEnvironment]:
    return EnvironmentService(db).get_environments()


@router.post("", dependencies=[Depends(only_for_admin)])
def create_environment(environment: Environment, db: Session = Depends(get_db_session)):
    EnvironmentService(db).create_environment(environment)


@router.get(
    "/{environment_id}/platforms/{platform_id}/services/{service_id}/config",
    dependencies=[Depends(only_for_admin)],
)
def get_environment_platform_service_config(
    environment_id: UUID,
    platform_id: UUID,
    service_id: UUID,
    db: Session = Depends(get_db_session),
) -> EnvPlatformServiceConfig:
    config = EnvironmentService(db).get_environment_platform_service_config(
        environment_id, platform_id, service_id
    )
    return EnvPlatformServiceConfig(config=config)


@router.get(
    "/{environment_id}/platforms/{platform_id}/config",
    dependencies=[Depends(only_for_admin)],
)
def get_environment_platform_config(
    environment_id: UUID,
    platform_id: UUID,
    db: Session = Depends(get_db_session),
) -> EnvPlatformConfig:
    config = EnvironmentService(db).get_environment_platform_config(
        environment_id, platform_id
    )
    return EnvPlatformConfig(config=config)
