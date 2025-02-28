from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.dependencies import only_for_admin
from app.roles.schema import CreateRole, Role
from app.roles.service import RoleService

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/{scope}")
def get_roles(scope: str, db: Session = Depends(get_db_session)) -> list[Role]:
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
def create_role(role: CreateRole, db: Session = Depends(get_db_session)) -> Role:
    return RoleService(db).create_role(role)


@router.put(
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
def update_role(role: Role, db: Session = Depends(get_db_session)) -> Role:
    return RoleService(db).update_role(role)


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
def remove_role(id: UUID, db: Session = Depends(get_db_session)) -> None:
    return RoleService(db).delete_role(id)
