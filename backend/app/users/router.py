from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.database import get_db_session
from app.users.schema import User
from app.users.schema_request import CanBecomeAdminUpdate, UserCreate
from app.users.schema_response import UsersGet
from app.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def get_users(db: Session = Depends(get_db_session)) -> Sequence[UsersGet]:
    return UserService(db).get_users()


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
    return UserService(db).remove_user(id)


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
    return UserService(db).create_user(user)


@router.post("/seen_tour")
def mark_tour_as_seen(
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> None:
    UserService(db).mark_tour_as_seen(user.id)


@router.put(
    "/can_become_admin",
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__CREATE_USER, EmptyResolver)),
    ],
)
def set_can_become_admin(
    request: CanBecomeAdminUpdate,
    db: Session = Depends(get_db_session),
) -> None:
    UserService(db).set_can_become_admin(request)
