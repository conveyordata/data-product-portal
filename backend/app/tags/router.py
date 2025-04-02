from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import Authorization, DataProductResolver
from app.database.database import get_db_session
from app.dependencies import only_for_admin
from app.tags.schema import Tag as TagGet
from app.tags.schema import TagCreate, TagUpdate
from app.tags.service import TagService

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("")
def get_tags(db: Session = Depends(get_db_session)) -> list[TagGet]:
    return TagService().get_tags(db)


@router.post(
    "",
    dependencies=[
        Depends(only_for_admin),
        Depends(
            Authorization.enforce(
                AuthorizationAction.GLOBAL__UPDATE_CONFIGURATION, DataProductResolver
            )
        ),
    ],
)
def create_tag(
    tag: TagCreate, db: Session = Depends(get_db_session)
) -> dict[str, UUID]:
    return TagService().create_tag(tag, db)


@router.put(
    "/{id}",
    dependencies=[
        Depends(only_for_admin),
        Depends(
            Authorization.enforce(
                AuthorizationAction.GLOBAL__UPDATE_CONFIGURATION, DataProductResolver
            )
        ),
    ],
)
def update_tag(id: UUID, tag: TagUpdate, db: Session = Depends(get_db_session)):
    return TagService().update_tag(id, tag, db)


@router.delete(
    "/{id}",
    dependencies=[
        Depends(only_for_admin),
        Depends(
            Authorization.enforce(
                AuthorizationAction.GLOBAL__UPDATE_CONFIGURATION, DataProductResolver
            )
        ),
    ],
)
def remove_tag(id: UUID, db: Session = Depends(get_db_session)):
    return TagService().remove_tag(id, db)
