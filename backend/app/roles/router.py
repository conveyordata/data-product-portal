from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization
from app.core.authz.resolvers import DataProductResolver
from app.database.database import get_db_session
from app.roles.auth import AuthRole
from app.roles.schema import CreateRole, Role, Scope, UpdateRole
from app.roles.service import RoleService

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/{scope}")
def get_roles(scope: Scope, db: Session = Depends(get_db_session)) -> Sequence[Role]:
    return RoleService(db).get_roles(scope)


@router.post(
    "",
    responses={
        200: {
            "description": "Role successfully created",
            "content": {
                "application/json": {"example": {"id": "random id of the new role"}}
            },
        },
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__UPDATE_ROLE_CONFIGURATION, DataProductResolver
            )
        ),
    ],
)
def create_role(
    request: CreateRole,
    db: Session = Depends(get_db_session),
) -> Role:
    role: Role = RoleService(db).create_role(request)
    AuthRole(role).sync()
    return role


@router.patch(
    "",
    responses={
        200: {
            "description": "Role successfully updated",
            "content": {
                "application/json": {"example": {"id": "id of the updated role"}}
            },
        },
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__UPDATE_ROLE_CONFIGURATION, DataProductResolver
            )
        ),
    ],
)
def update_role(
    request: UpdateRole,
    db: Session = Depends(get_db_session),
) -> Role:
    role: Role = RoleService(db).update_role(request)
    AuthRole(role).sync()
    return role


@router.delete(
    "/{id}",
    responses={
        404: {
            "description": "Role not found",
            "content": {"application/json": {"example": {"detail": "Role not found"}}},
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__UPDATE_ROLE_CONFIGURATION, DataProductResolver
            )
        ),
    ],
)
def remove_role(id: UUID, db: Session = Depends(get_db_session)) -> None:
    role: Role = RoleService(db).delete_role(id)
    AuthRole(role).remove()
