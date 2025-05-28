from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.database.database import get_db_session
from app.notifications.schema_response import NotificationGet
from app.notifications.service import NotificationService
from app.users.schema import User

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def get_user_notifications(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> list[NotificationGet]:
    return NotificationService().get_user_notifications(db, authenticated_user)


@router.delete("/all")
def remove_all_user_notifications(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return NotificationService().remove_all_notifications(db, authenticated_user)


@router.delete("/{id}")
def remove_user_notification(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return NotificationService().remove_notification(id, db, authenticated_user)
