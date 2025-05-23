from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.database import get_db_session
from app.users.schema_request import UserCreate
from app.users.schema_response import UsersGet
from app.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def get_users(db: Session = Depends(get_db_session)) -> list[UsersGet]:
    return UserService().get_users(db)


@router.delete(
    "/{id}",
    responses={
        404: {
            "description": "User not found",
            "content": {
                "application/json": {"example": {"detail": "User email not found"}}
            },
        }
    },
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__DELETE_USER, EmptyResolver)),
    ],
)
def remove_user(id: UUID, db: Session = Depends(get_db_session)) -> None:
    return UserService().remove_user(id, db)


@router.post(
    "",
    responses={
        200: {
            "description": "User successfully created",
            "content": {
                "application/json": {"example": {"id": "random id of the new user"}}
            },
        },
    },
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__CREATE_USER, EmptyResolver)),
    ],
)
def create_user(
    user: UserCreate, db: Session = Depends(get_db_session)
) -> dict[str, UUID]:
    return UserService().create_user(user, db)
