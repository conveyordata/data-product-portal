from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.authorization.roles.auth import AuthRole
from app.authorization.roles.schema import (
    CreateRole,
    GetRolesResponse,
    Role,
    Scope,
    UpdateRole,
)
from app.authorization.roles.service import RoleService
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.database import get_db_session

router = APIRouter(tags=["Authorization - Roles"], prefix="/v2/authz/roles")


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
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
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
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def remove_role(id: UUID, db: Session = Depends(get_db_session)) -> None:
    role: Role = RoleService(db).delete_role(id)
    AuthRole(role).remove()


@router.put(
    "/{id}",
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
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def update_role(
    id: UUID,
    request: UpdateRole,
    db: Session = Depends(get_db_session),
) -> Role:
    role: Role = RoleService(db).update_role(id, request)
    AuthRole(role).sync()
    return role


@router.get("/{scope}")
def get_roles(scope: Scope, db: Session = Depends(get_db_session)) -> GetRolesResponse:
    return GetRolesResponse(roles=RoleService(db).get_roles(scope))
