from uuid import UUID

from app.events.schema_response import GetEventHistoryResponseItemOld
from app.shared.schema import ORMModel
from app.users.schema import User


class BaseNotificationGet(ORMModel):
    id: UUID
    event_id: UUID
    user_id: UUID


class NotificationGet(BaseNotificationGet):
    event: GetEventHistoryResponseItemOld
    user: User
