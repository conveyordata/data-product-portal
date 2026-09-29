from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.configuration.output_port_access_types.schema_request import (
    OutputPortAccessTypeCreate,
    OutputPortAccessTypeUpdate,
)
from app.configuration.output_port_access_types.schema_response import (
    CreateOutputPortAccessTypeResponse,
    OutputPortAccessTypesGet,
    UpdateOutputPortAccessTypeResponse,
)
from app.configuration.output_port_access_types.service import (
    OutputPortAccessTypeService,
)
from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.deps import get_db_session
from app.users.model import User

router = APIRouter(
    tags=["Configuration - Output Port access types"],
    prefix="/v2/configuration/output_port_access_types",
)


@router.get("")
def get_output_port_access_types(
    db: Session = Depends(get_db_session, scope="function"),
    user: User = Depends(get_authenticated_user),
) -> OutputPortAccessTypesGet:
    return OutputPortAccessTypesGet(
        output_port_access_types=OutputPortAccessTypeService(
            db
        ).get_output_port_access_types(user)
    )


@router.post(
    "",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def create_output_port_access_type(
    output_port_access_type: OutputPortAccessTypeCreate,
    db: Session = Depends(get_db_session, scope="function"),
) -> CreateOutputPortAccessTypeResponse:
    return OutputPortAccessTypeService(db).create_output_port_access_type(
        output_port_access_type
    )


@router.put(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def update_output_port_access_type(
    id: UUID,
    output_port_access_type: OutputPortAccessTypeUpdate,
    db: Session = Depends(get_db_session, scope="function"),
) -> UpdateOutputPortAccessTypeResponse:
    return OutputPortAccessTypeService(db).update_output_port_access_type(
        id, output_port_access_type
    )


@router.delete(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def remove_output_port_access_type(
    id: UUID,
    db: Session = Depends(get_db_session, scope="function"),
) -> None:
    OutputPortAccessTypeService(db).delete_output_port_access_type(id)
