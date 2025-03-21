from app.notifications.notification_types import NotificationTypes
from app.shared.schema import ORMModel


class Notification(ORMModel):
    configuration_type: NotificationTypes
