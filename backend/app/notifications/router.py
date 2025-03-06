from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.notifications.schema import (
    Notification,
)
from app.notifications.service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])  # TODO tags?


@router.get("")
def get_notifications(db: Session = Depends(get_db_session)) -> list[Notification]:
    return NotificationService().get_notifications(db)
