from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.configuration.environments.schema_request import EnvironmentUpdateGlobal
from app.configuration.environments.schema_response import (
    Environment,
    EnvironmentsGet,
)
from app.configuration.environments.service import EnvironmentService
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.deps import get_db_session

router = APIRouter(
    tags=["Configuration - Environments"], prefix="/v2/configuration/environments"
)


@router.get("/{id}")
def get_environment(
    id: UUID, db: Session = Depends(get_db_session, scope="function")
) -> Environment:
    return EnvironmentService(db).get_environment(id)


@router.get("")
def get_environments(
    db: Session = Depends(get_db_session, scope="function"),
) -> EnvironmentsGet:
    return EnvironmentsGet(environments=EnvironmentService(db).get_environments())


@router.patch(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def update_environment_is_global(
    id: UUID,
    environment_update: EnvironmentUpdateGlobal,
    db: Session = Depends(get_db_session, scope="function"),
) -> Environment:
    return EnvironmentService(db).update_is_global(id, environment_update.is_global)
