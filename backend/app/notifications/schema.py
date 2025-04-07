from uuid import UUID

from app.notifications.notification_types import NotificationTypes
from app.notifications.schema_union import NotificationReferenceUnion
from app.shared.schema import ORMModel


class Notification(ORMModel):
    id: UUID
    configuration_type: NotificationTypes
    reference_id: UUID
    reference: NotificationReferenceUnion
