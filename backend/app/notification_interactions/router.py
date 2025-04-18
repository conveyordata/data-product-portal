from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.database.database import get_db_session
from app.dependencies import only_notification_interaction_owner
from app.notification_interactions.schema_get import (
    NotificationInteractionGet,
)
from app.notification_interactions.service import NotificationInteractionService
from app.users.schema import User

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def get_user_notification_interactions(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> list[NotificationInteractionGet]:
    return NotificationInteractionService().get_user_notification_interactions(
        db, authenticated_user
    )


@router.delete("/{id}", dependencies=[Depends(only_notification_interaction_owner)])
def remove_user_notification(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return NotificationInteractionService().remove_notification_interaction(
        id, db, authenticated_user
    )
