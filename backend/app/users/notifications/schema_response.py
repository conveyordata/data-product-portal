from typing import Sequence
from uuid import UUID

from app.events.schema_response import (
    GetEventHistoryResponseItem,
    GetEventHistoryResponseItemOld,
)
from app.shared.schema import ORMModel
from app.users.schema import User


class BaseNotificationGet(ORMModel):
    id: UUID
    event_id: UUID
    user_id: UUID


class GetUserNotificationsResponseItem(BaseNotificationGet):
    event: GetEventHistoryResponseItem
    user: User


class NotificationGet(BaseNotificationGet):
    event: GetEventHistoryResponseItemOld
    user: User

    def convert(self) -> GetUserNotificationsResponseItem:
        return GetUserNotificationsResponseItem(
            **self.model_dump(exclude={"event"}), event=self.event.convert()
        )


class GetUserNotificationsResponse(ORMModel):
    notifications: Sequence[GetUserNotificationsResponseItem]
