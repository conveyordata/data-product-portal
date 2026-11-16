from uuid import UUID

from fastapi import APIRouter, Depends

from app.configuration.tags.schema_request import TagCreate, TagUpdate
from app.configuration.tags.schema_response import (
    CreateTagResponse,
    TagsGet,
    UpdateTagResponse,
)
from app.configuration.tags.service import TagService
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.deps import DbSession

router = APIRouter(tags=["Configuration - Tags"], prefix="/v2/configuration/tags")


@router.post(
    "",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def create_tag(tag: TagCreate, db: DbSession) -> CreateTagResponse:
    return TagService(db).create_tag(tag)


@router.put(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def update_tag(
    id: UUID,
    tag: TagUpdate,
    db: DbSession,
) -> UpdateTagResponse:
    return TagService(db).update_tag(id, tag)


@router.delete(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def remove_tag(id: UUID, db: DbSession) -> None:
    return TagService(db).remove_tag(id)


@router.get("")
def get_tags(
    db: DbSession,
) -> TagsGet:
    return TagsGet(tags=TagService(db).get_tags())
