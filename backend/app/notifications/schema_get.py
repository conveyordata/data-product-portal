from uuid import UUID

from app.notifications.schema_union import NotificationConfigurationGet
from app.shared.schema import ORMModel


class NotificationGet(ORMModel):
    id: UUID
    description: str
    configuration: NotificationConfigurationGet
