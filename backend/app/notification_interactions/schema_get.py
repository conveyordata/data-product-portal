from datetime import datetime
from typing import Optional
from uuid import UUID

from app.notifications.schema_union import NotificationConfiguration
from app.shared.schema import ORMModel
from app.users.schema import User


class NotificationInteractionGet(ORMModel):
    id: UUID
    notification_id: UUID
    notification: NotificationConfiguration
    user_id: UUID
    user: User
    last_seen: Optional[datetime]
    last_interaction: Optional[datetime]
