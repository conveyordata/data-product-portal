from typing import Sequence
from uuid import UUID

from app.events.schema_response import GetEventHistoryResponseItem
from app.shared.schema import ORMModel
from app.users.schema import User


class BaseNotificationGet(ORMModel):
    id: UUID
    event_id: UUID
    user_id: UUID


class GetUserNotificationsResponseItem(BaseNotificationGet):
    event: GetEventHistoryResponseItem
    user: User


class GetUserNotificationsResponse(ORMModel):
    notifications: Sequence[GetUserNotificationsResponseItem]
