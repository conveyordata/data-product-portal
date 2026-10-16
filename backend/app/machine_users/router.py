from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.deps import get_db_session
from app.identities.schema_request import (
    IdentityBatchCreateRequest,
    IdentityBatchDeleteRequest,
)
from app.identities.schema_response import IdentityBatchCreateResponse
from app.machine_users.schema_request import (
    MachineUserCreate,
    MachineUserUpdate,
)
from app.machine_users.schema_response import (
    MachineUserCreateResponse,
    MachineUserGet,
    MachineUsersGetResponse,
    MachineUserUpdateResponse,
)
from app.machine_users.service import MachineUserService

router = APIRouter(
    tags=["Machine Users"],
    prefix="/v2/machine-users",
)


@router.get("")
def get_machine_users(
    db: Session = Depends(get_db_session, scope="function"),
) -> MachineUsersGetResponse:
    return MachineUsersGetResponse(
        machine_users=MachineUserService(db).get_machine_users(),
    )


@router.get(
    "/{id}",
    responses={
        404: {
            "description": "Machine user not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Required machine user does not exist"}
                }
            },
        }
    },
)
def get_machine_user(
    id: UUID,
    db: Session = Depends(get_db_session, scope="function"),
) -> MachineUserGet:
    return MachineUserService(db).get_machine_user(id)


@router.post(
    "",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__CREATE_MACHINE_USER,
                EmptyResolver,
            )
        ),
    ],
    responses={
        400: {
            "description": "Machine user external ID already exists",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "A machine user with this external ID already exists."
                    }
                }
            },
        },
    },
)
def create_machine_user(
    machine_user: MachineUserCreate,
    db: Session = Depends(get_db_session, scope="function"),
) -> MachineUserCreateResponse:
    return MachineUserService(db).create_machine_user(machine_user)


@router.put(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__UPDATE_MACHINE_USER,
                EmptyResolver,
            )
        ),
    ],
    responses={
        404: {
            "description": "Machine user not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Required machine user does not exist"}
                }
            },
        }
    },
)
def update_machine_user(
    id: UUID,
    machine_user: MachineUserUpdate,
    db: Session = Depends(get_db_session, scope="function"),
) -> MachineUserUpdateResponse:
    return MachineUserService(db).update_machine_user(id, machine_user)


@router.post(
    "/batch",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__CREATE_MACHINE_USER,
                EmptyResolver,
            )
        ),
    ],
)
def create_machine_users_batch(
    request: IdentityBatchCreateRequest,
    db: Session = Depends(get_db_session, scope="function"),
) -> IdentityBatchCreateResponse:
    return MachineUserService(db).create_machine_users_batch(request.items)


@router.delete(
    "/batch",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__DELETE_MACHINE_USER,
                EmptyResolver,
            )
        ),
    ],
)
def delete_machine_users_batch(
    request: IdentityBatchDeleteRequest,
    db: Session = Depends(get_db_session, scope="function"),
) -> None:
    MachineUserService(db).delete_machine_users_batch(request.ids)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__DELETE_MACHINE_USER,
                EmptyResolver,
            )
        ),
    ],
    responses={
        404: {
            "description": "Machine user not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Required machine user does not exist"}
                }
            },
        }
    },
)
def delete_machine_user(
    id: UUID,
    db: Session = Depends(get_db_session, scope="function"),
) -> None:
    MachineUserService(db).delete_machine_user(id)
