from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.deps import get_db_session
from app.groups.schema_request import GroupCreate, GroupUpdate
from app.groups.schema_response import (
    GroupCreateResponse,
    GroupGet,
    GroupsGetResponse,
    GroupUpdateResponse,
)
from app.groups.service import GroupService

router = APIRouter(tags=["Groups"], prefix="/v2/groups")


@router.get("")
def get_groups(
    db: Session = Depends(get_db_session, scope="function"),
) -> GroupsGetResponse:
    return GroupsGetResponse(groups=GroupService(db).get_groups())


@router.get("/{id}")
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
)
def update_group(
    id: UUID,
    group: GroupUpdate,
    db: Session = Depends(get_db_session, scope="function"),
) -> GroupUpdateResponse:
    return GroupService(db).update_group(id, group)


@router.delete(
    "/{id}",
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__DELETE_GROUP, EmptyResolver)),
    ],
)
def delete_group(
    id: UUID,
    db: Session = Depends(get_db_session, scope="function"),
) -> None:
    GroupService(db).delete_group(group_id=id)