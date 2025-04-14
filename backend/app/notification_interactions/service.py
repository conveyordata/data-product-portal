from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, joinedload

from app.notification_interactions.model import NotificationInteraction
from app.notification_interactions.schema_get import NotificationInteractionGet
from app.users.schema import User


class NotificationInteractionService:

    def get_user_notification_interactions(
        self, db: Session, authenticated_user: User
    ) -> list[NotificationInteractionGet]:
        return db.scalars(
            select(NotificationInteraction)
            .options(
                joinedload(NotificationInteraction.notification),
                joinedload(NotificationInteraction.user),
            )
            .where(NotificationInteraction.user_id == authenticated_user.id)
            .order_by(desc(NotificationInteraction.created_on))
        ).all()

    def remove_notification_interaction(
        self, id: UUID, db: Session, authenticated_user: User
    ):
        notification_interaction = db.get(
            NotificationInteraction,
            id,
        )
        if not notification_interaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification {id} not found",
            )
        if notification_interaction.user_id != authenticated_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Notification {id} belongs to another user",
            )
        db.delete(notification_interaction)
        db.commit()
