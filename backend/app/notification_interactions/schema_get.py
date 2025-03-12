from datetime import datetime
from uuid import UUID

from app.notifications.schema_union import NotificationConfigurationGet
from app.shared.schema import ORMModel
from app.users.schema import User


class NotificationInteractionGet(ORMModel):
    id: UUID
    notification_id: UUID
    notification: NotificationConfigurationGet
    user_id: UUID  # redundant?
    user: User
    last_seen: datetime | None
    last_interaction: datetime | None
