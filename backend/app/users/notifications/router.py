from uuid import UUID

from fastapi import APIRouter

from app.core.auth.auth import AuthenticatedUser
from app.database.deps import DbSession
from app.users.notifications.schema_response import (
    GetUserNotificationsResponse,
    GetUserNotificationsResponseItem,
)
from app.users.notifications.service import NotificationService

router = APIRouter(
    tags=["Users - Notifications"], prefix="/v2/users/current/notifications"
)


@router.delete("/all")
def remove_all_user_notifications(
    db: DbSession,
    authenticated_user: AuthenticatedUser,
) -> None:
    return NotificationService(db).remove_all_notifications(authenticated_user)


@router.delete("/{id}")
def remove_user_notification(
    id: UUID,
    db: DbSession,
    authenticated_user: AuthenticatedUser,
) -> None:
    return NotificationService(db).remove_notification(id, authenticated_user)


@router.get("")
def get_user_notifications(
    db: DbSession,
    authenticated_user: AuthenticatedUser,
) -> GetUserNotificationsResponse:
    notifications = [
        GetUserNotificationsResponseItem.model_validate(event)
        for event in NotificationService(db).get_user_notifications(authenticated_user)
    ]
    return GetUserNotificationsResponse(notifications=notifications)
