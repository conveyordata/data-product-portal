from uuid import UUID

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.dependencies import only_for_admin
from app.environments.enums import PlatformTypes
from app.environments.schema import CreatePlatform, Environment, Platform
from app.environments.service import EnvironmentService

router = APIRouter(prefix="/envs", tags=["environments"])


@router.get("")
def get_environments(db: Session = Depends(get_db_session)) -> list[Environment]:
    return EnvironmentService(db).get_environments()


@router.post("")
def create_environment(environment: Environment, db: Session = Depends(get_db_session)):
    EnvironmentService(db).create_environment(environment)


@router.put(
    "/{environment}/platforms",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(only_for_admin)],
)
def add_or_update_environment_settings(
    environment: str,
    platform: CreatePlatform,
    db: Session = Depends(get_db_session),
):
    EnvironmentService(db).add_or_update_settings(environment, platform)


@router.delete(
    "/platforms/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(only_for_admin)],
)
def delete_environment_settings(
    platform_id: UUID = Path(alias="id"),
    db: Session = Depends(get_db_session),
):
    EnvironmentService(db).delete_settings(platform_id)


@router.get("/{environment}/platforms", dependencies=[Depends(only_for_admin)])
def get_all_environment_platforms(
    environment: str,
    db: Session = Depends(get_db_session),
) -> list[Platform]:
    return EnvironmentService(db).get_all_environment_platforms(environment)


@router.get("/{environment}/platforms/{name}", dependencies=[Depends(only_for_admin)])
def get_environment_platform(
    environment: str,
    name: PlatformTypes,
    db: Session = Depends(get_db_session),
) -> Platform:
    return EnvironmentService(db).get_environment_platform(environment, name)
