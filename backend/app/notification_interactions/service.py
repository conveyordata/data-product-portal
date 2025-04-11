from sqlalchemy import asc, select
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
            .order_by(asc(NotificationInteraction.last_seen))
        ).all()
