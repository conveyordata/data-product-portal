from uuid import UUID

from app.notifications.schema import Notification
from app.shared.schema import ORMModel
from app.users.schema import User


class NotificationInteractionGet(ORMModel):
    id: UUID
    notification_id: UUID
    notification: Notification
    user_id: UUID
    user: User
