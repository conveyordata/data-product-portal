from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.dependencies import only_for_admin
from app.environments.schema import (
    CreateConfigSchema,
    Environment,
    EnvPlatformServiceConfigGet,
    GetEnvironment,
)
from app.environments.service import EnvironmentService

router = APIRouter(prefix="/envs", tags=["environments"])


@router.get("", dependencies=[Depends(only_for_admin)])
def get_environments(db: Session = Depends(get_db_session)) -> Sequence[GetEnvironment]:
    return EnvironmentService(db).get_environments()


@router.get("/{environment_id}", dependencies=[Depends(only_for_admin)])
def get_environment(
    environment_id: UUID, db: Session = Depends(get_db_session)
) -> GetEnvironment:
    return EnvironmentService(db).get_environment_by_id(environment_id)


@router.post(
    "", dependencies=[Depends(only_for_admin)], status_code=status.HTTP_201_CREATED
)
def create_environment(environment: Environment, db: Session = Depends(get_db_session)):
    EnvironmentService(db).create_environment(environment)


@router.get("/{environment_id}/configs", dependencies=[Depends(only_for_admin)])
def get_environment_configs(
    environment_id: UUID,
    db: Session = Depends(get_db_session),
) -> Sequence[EnvPlatformServiceConfigGet]:
    return EnvironmentService(db).get_environment_configs(environment_id)


@router.post(
    "/{environment_id}/configs",
    dependencies=[Depends(only_for_admin)],
    status_code=status.HTTP_201_CREATED,
)
def create_environment_platform_service_config(
    environment_id: UUID,
    config_data: CreateConfigSchema,
    db: Session = Depends(get_db_session),
):
    EnvironmentService(db).create_config(
        environment_id,
        config_data.platform_id,
        config_data.service_id,
        config_data.config,
    )


@router.get(
    "/configs/{config_id}",
    dependencies=[Depends(only_for_admin)],
)
def get_environment_config_by_id(
    config_id: UUID, db: Session = Depends(get_db_session)
) -> EnvPlatformServiceConfigGet:
    return EnvironmentService(db).get_environment_config_by_id(config_id)
