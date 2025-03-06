from app.notifications.notification_types import NotificationTypes
from app.shared.schema import ORMModel


class BaseNotificationConfiguration(ORMModel):
    configuration_type: NotificationTypes
