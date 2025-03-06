from uuid import UUID

from app.notification_interactions.schema import NotificationInteraction
from app.notifications.schema_union import NotificationConfiguration
from app.shared.schema import ORMModel


class Notification(ORMModel):
    id: UUID
    description: str
    configuration: NotificationConfiguration
    notification_interactions: list[NotificationInteraction]
