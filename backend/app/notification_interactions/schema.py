from uuid import UUID

from app.shared.schema import ORMModel
from app.users.schema import User


class NotificationInteraction(ORMModel):
    id: UUID
    notification_id: UUID
    user_id: UUID
    user: User
