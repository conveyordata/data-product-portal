from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.auth.auth import AuthenticatedUser, authorize_user
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.deps import DbSession
from app.groups.schema_response import GroupsGetResponse
from app.identities.schema_request import (
    IdentityBatchCreateRequest,
    IdentityBatchDeleteRequest,
)
from app.identities.schema_response import IdentityBatchCreateResponse
from app.users.schema import User
from app.users.schema_request import CanBecomeAdminUpdate, UserCreate
from app.users.schema_response import (
    GetUsersResponse,
    MyRequestsResponse,
    PendingActionResponse,
    UserCreateResponse,
)
from app.users.service import UserService

router = APIRouter(tags=["Users"], prefix="/v2/users")


@router.get("")
def get_users(
    db: DbSession,
) -> GetUsersResponse:
    return GetUsersResponse(users=UserService(db).get_users())


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
def create_user(user: UserCreate, db: DbSession) -> UserCreateResponse:
    return UserService(db).create_user(user)


@router.post(
    "/batch",
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__CREATE_USER, EmptyResolver)),
    ],
)
def create_users_batch(
    request: IdentityBatchCreateRequest[UserCreate],
    db: DbSession,
) -> IdentityBatchCreateResponse:
    return UserService(db).create_users_batch(request.items)


@router.delete(
    "/batch",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__DELETE_USER, EmptyResolver)),
    ],
)
def remove_users_batch(
    request: IdentityBatchDeleteRequest,
    db: DbSession,
) -> None:
    UserService(db).remove_users_batch(request.ids)


@router.put(
    "/set_can_become_admin",
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__CREATE_USER, EmptyResolver)),
    ],
)
def set_can_become_admin(
    request: CanBecomeAdminUpdate,
    db: DbSession,
) -> None:
    UserService(db).set_can_become_admin(request)


@router.get("/current")
def get_current_user(authorized_user: Annotated[User, Depends(authorize_user)]) -> User:
    return authorized_user


@router.get("/current/groups")
def get_current_user_groups(
    db: DbSession,
    authenticated_user: AuthenticatedUser,
) -> GroupsGetResponse:
    return GroupsGetResponse(groups=UserService(db).get_groups(authenticated_user.id))


@router.get("/current/my_requests")
def get_user_requests(
    db: DbSession,
    authenticated_user: AuthenticatedUser,
    hide_old_inactive: Annotated[
        bool, Query(description="Filter out inactive requests older than 30 days")
    ] = True,
) -> MyRequestsResponse:
    return UserService(db).get_user_requests(authenticated_user, hide_old_inactive)


@router.get("/current/pending_actions")
def get_user_pending_actions(
    db: DbSession,
    authenticated_user: AuthenticatedUser,
) -> PendingActionResponse:
    return UserService(db).get_user_pending_actions(authenticated_user)


@router.post("/current/seen_tour")
def mark_tour_as_seen(
    db: DbSession,
    user: AuthenticatedUser,
) -> None:
    UserService(db).mark_tour_as_seen(user.id)


@router.get(
    "/{id}/groups",
    responses={
        404: {
            "description": "User not found",
            "content": {"application/json": {"example": {"detail": "User not found"}}},
        }
    },
)
def get_user_groups(
    id: UUID,
    db: DbSession,
) -> GroupsGetResponse:
    return GroupsGetResponse(groups=UserService(db).get_groups(id))


@router.delete(
    "/{id}",
    responses={
        404: {
            "description": "User not found",
            "content": {"application/json": {"example": {"detail": "User not found"}}},
        }
    },
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__DELETE_USER, EmptyResolver)),
    ],
)
def remove_user(id: UUID, db: DbSession) -> None:
    return UserService(db).remove_user(id)
