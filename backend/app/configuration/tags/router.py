from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.configuration.tags.schema_request import TagCreate, TagUpdate
from app.configuration.tags.schema_response import (
    CreateTagResponse,
    TagsGet,
    TagsGetItem,
    UpdateTagResponse,
)
from app.configuration.tags.service import TagService
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.database import get_db_session

router = APIRouter()


@router.post(
    "",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def create_tag(
    tag: TagCreate, db: Session = Depends(get_db_session)
) -> CreateTagResponse:
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
    id: UUID, tag: TagUpdate, db: Session = Depends(get_db_session)
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
def remove_tag(id: UUID, db: Session = Depends(get_db_session)) -> None:
    return TagService(db).remove_tag(id)


_router = router
router = APIRouter(tags=["Configuration - Tags"])
router.include_router(_router, prefix="/tags", deprecated=True)
router.include_router(_router, prefix="/v2/configuration/tags")


@router.get("/tags", deprecated=True)
def get_tags_old(db: Session = Depends(get_db_session)) -> Sequence[TagsGetItem]:
    return get_tags(db).tags


@router.get("/v2/configuration/tags")
def get_tags(db: Session = Depends(get_db_session)) -> TagsGet:
    return TagsGet(tags=TagService(db).get_tags())
