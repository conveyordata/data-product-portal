from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.tags.schema import Tag as TagGet
from app.tags.schema import TagCreate, TagUpdate
from app.tags.service import TagService

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("")
def get_tags(db: Session = Depends(get_db_session)) -> list[TagGet]:
    return TagService().get_tags(db)


@router.post("")
def create_tag(
    tag: TagCreate, db: Session = Depends(get_db_session)
) -> dict[str, UUID]:
    return TagService().create_tag(tag, db)


@router.put("/{id}")
def update_tag(id: UUID, tag: TagUpdate, db: Session = Depends(get_db_session)):
    return TagService().update_tag(id, tag, db)


@router.delete("/{id}")
def remove_tag(id: UUID, db: Session = Depends(get_db_session)):
    return TagService().remove_tag(id, db)
