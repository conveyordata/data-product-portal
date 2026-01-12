from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.database.database import get_db_session
from app.users.notifications.schema_response import (
    GetUserNotificationsResponse,
    NotificationGet,
)
from app.users.notifications.service import NotificationService
from app.users.schema import User

router = APIRouter()


@router.delete("/all")
def remove_all_user_notifications(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    return NotificationService(db).remove_all_notifications(authenticated_user)


@router.delete("/{id}")
def remove_user_notification(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    return NotificationService(db).remove_notification(id, authenticated_user)


_router = router
router = APIRouter(tags=["Users - Notifications"])
old_route = "/notifications"
route = "/v2/users/current/notifications"

router.include_router(_router, prefix=old_route, deprecated=True)
router.include_router(_router, prefix=route)


@router.get(old_route, deprecated=True)
def get_user_notifications_old(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> Sequence[NotificationGet]:
    return NotificationService(db).get_user_notifications(authenticated_user)


@router.get(route)
def get_user_notifications(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> GetUserNotificationsResponse:
    events = [
        NotificationGet.model_validate(event).convert()
        for event in get_user_notifications_old(db, authenticated_user)
    ]
    return GetUserNotificationsResponse(events=events)
