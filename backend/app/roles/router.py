from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.dependencies import only_for_admin
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
    dependencies=[Depends(only_for_admin)],
)
def create_role(
    request: CreateRole,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
) -> Role:
    role: Role = RoleService(db).create_role(request)
    background_tasks.add_task(AuthRole(role).sync)
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
    dependencies=[Depends(only_for_admin)],
)
def update_role(
    request: UpdateRole,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
) -> Role:
    role: Role = RoleService(db).update_role(request)
    background_tasks.add_task(AuthRole(role).sync)
    return role


@router.delete(
    "/{id}",
    responses={
        404: {
            "description": "Role not found",
            "content": {"application/json": {"example": {"detail": "Role not found"}}},
        }
    },
    dependencies=[Depends(only_for_admin)],
)
def remove_role(
    id: UUID, background_tasks: BackgroundTasks, db: Session = Depends(get_db_session)
) -> None:
    role: Role = RoleService(db).delete_role(id)
    background_tasks.add_task(AuthRole(role).remove)
