from uuid import UUID

from fastapi import APIRouter, Depends

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
from app.core.auth.auth import AuthenticatedUser
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.deps import DbSession

router = APIRouter(
    tags=["Configuration - Output Port access types"],
    prefix="/v2/configuration/output_port_access_types",
)


@router.get("")
def get_output_port_access_types(
    db: DbSession,
    user: AuthenticatedUser,
    include_output_port_count: bool = False,
) -> OutputPortAccessTypesGet:
    access_types = OutputPortAccessTypeService(db).get_output_port_access_types(
        user, include_output_port_count
    )
    return OutputPortAccessTypesGet(output_port_access_types=access_types)


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
    db: DbSession,
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
    db: DbSession,
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
    db: DbSession,
) -> None:
    OutputPortAccessTypeService(db).delete_output_port_access_type(id)
