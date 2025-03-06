from datetime import datetime
from uuid import UUID

from app.shared.schema import ORMModel
from app.users.schema import User


class NotificationInteraction(ORMModel):  # no base?
    id: UUID
    notification_id: UUID
    user_id: UUID  # redundant?
    user: User
    last_seen: datetime | None
    last_interaction: datetime | None
