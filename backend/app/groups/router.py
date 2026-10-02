import asyncio
from collections.abc import AsyncIterator
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.deps import get_db_session
from app.groups.schema_request import (
    GroupCreate,
    GroupMembersAdd,
    GroupMembersRemove,
    GroupMembersReplace,
    GroupUpdate,
)
from app.groups.schema_response import (
    GroupCreateResponse,
    GroupGet,
    GroupMembershipsGetResponse,
    GroupsGetResponse,
    GroupUpdateResponse,
)
from app.groups.service import GroupService

router = APIRouter(tags=["Groups"], prefix="/v2/groups")
_group_members_replace_locks: dict[UUID, asyncio.Lock] = {}


async def _serialize_group_members_replacement(
    id: UUID,
) -> AsyncIterator[None]:
    """
    Used to enforce locking on group members replacement.
    """
    lock = _group_members_replace_locks.setdefault(id, asyncio.Lock())
    async with lock:
        yield


@router.get("")
def get_groups(
    db: Session = Depends(get_db_session, scope="function"),
) -> GroupsGetResponse:
    return GroupsGetResponse(groups=GroupService(db).get_groups())


@router.get(
    "/{id}",
    responses={
        404: {
            "description": "Group not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Required group does not exist"}
                }
            },
        }
    },
)
def get_group(
    id: UUID,
    db: Session = Depends(get_db_session, scope="function"),
) -> GroupGet:
    return GroupService(db).get_group(id)


@router.post(
    "",
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__CREATE_GROUP, EmptyResolver)),
    ],
    responses={
        400: {
            "description": "Group external ID already exists",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "A group with this external ID already exists."
                    }
                }
            },
        },
        404: {
            "description": "Group not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Required group does not exist"}
                }
            },
        },
    },
)
def create_group(
    group: GroupCreate,
    db: Session = Depends(get_db_session, scope="function"),
) -> GroupCreateResponse:
    return GroupService(db).create_group(group)


@router.put(
    "/{id}",
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__UPDATE_GROUP, EmptyResolver)),
    ],
    responses={
        404: {
            "description": "Group not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Required group does not exist"}
                }
            },
        }
    },
)
def update_group(
    id: UUID,
    group: GroupUpdate,
    db: Session = Depends(get_db_session, scope="function"),
) -> GroupUpdateResponse:
    return GroupService(db).update_group(id, group)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__DELETE_GROUP, EmptyResolver)),
    ],
    responses={
        404: {
            "description": "Group not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Required group does not exist"}
                }
            },
        }
    },
)
def delete_group(
    id: UUID,
    db: Session = Depends(get_db_session, scope="function"),
) -> None:
    GroupService(db).delete_group(group_id=id)


@router.get(
    "/{id}/members",
    responses={
        404: {
            "description": "Group not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Required group does not exist"}
                }
            },
        }
    },
)
def get_group_members(
    id: UUID,
    db: Session = Depends(get_db_session, scope="function"),
) -> GroupMembershipsGetResponse:
    return GroupMembershipsGetResponse(
        members=GroupService(db).get_members(id),
    )


@router.post(
    "/{id}/members",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__UPDATE_GROUP,
                EmptyResolver,
            )
        ),
    ],
    responses={
        400: {
            "description": "Invalid group member identities",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "All member identities must exist and be users or machine users."
                    }
                }
            },
        },
        404: {
            "description": "Group not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Required group does not exist"}
                }
            },
        },
    },
)
def add_group_members(
    id: UUID,
    request: GroupMembersAdd,
    db: Session = Depends(get_db_session, scope="function"),
) -> None:
    GroupService(db).add_members(
        group_id=id,
        member_identity_ids=request.member_identity_ids,
    )


@router.put(
    "/{id}/members",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__UPDATE_GROUP,
                EmptyResolver,
            )
        ),
        Depends(_serialize_group_members_replacement, scope="request"),
    ],
    responses={
        400: {
            "description": "Invalid group member identities",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "All member identities must exist and be users or machine users."
                    }
                }
            },
        },
        404: {
            "description": "Group not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Required group does not exist"}
                }
            },
        },
    },
)
def replace_group_members(
    id: UUID,
    request: GroupMembersReplace,
    db: Session = Depends(get_db_session, scope="function"),
) -> None:
    """
    Because the service method performs add and replace operations internally,
    a lock is used to ensure that only one request is processed at a time.
    """
    GroupService(db).replace_members(
        group_id=id,
        member_identity_ids=request.member_identity_ids,
    )


@router.delete(
    "/{id}/members",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__UPDATE_GROUP,
                EmptyResolver,
            )
        ),
    ],
    responses={
        404: {
            "description": "Group not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Required group does not exist"}
                }
            },
        },
    },
)
def remove_group_members(
    id: UUID,
    request: GroupMembersRemove,
    db: Session = Depends(get_db_session, scope="function"),
) -> None:
    GroupService(db).remove_members(
        group_id=id,
        member_identity_ids=request.member_identity_ids,
    )
