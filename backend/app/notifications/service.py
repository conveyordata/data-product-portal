from sqlalchemy.orm import Session

from app.notifications.model import Notification as NotificationModel
from app.notifications.schema import Notification


class NotificationService:
    def get_notifications(self, db: Session) -> list[Notification]:
        notifications = db.query(NotificationModel).all()
        return notifications
