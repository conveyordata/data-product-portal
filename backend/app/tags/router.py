from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.database import get_db_session
from app.tags.schema_request import TagCreate, TagUpdate
from app.tags.schema_response import TagsGet
from app.tags.service import TagService

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("")
def get_tags(db: Session = Depends(get_db_session)) -> Sequence[TagsGet]:
    return TagService(db).get_tags()


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
) -> dict[str, UUID]:
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
) -> dict[str, UUID]:
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
