from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_event_history_response_item import GetEventHistoryResponseItem
    from ..models.user import User


T = TypeVar("T", bound="GetUserNotificationsResponseItem")


@_attrs_define
class GetUserNotificationsResponseItem:
    """
    Attributes:
        id (UUID):
        event_id (UUID):
        user_id (UUID):
        event (GetEventHistoryResponseItem):
        user (User):
    """

    id: UUID
    event_id: UUID
    user_id: UUID
    event: GetEventHistoryResponseItem
    user: User
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        event_id = str(self.event_id)

        user_id = str(self.user_id)

        event = self.event.to_dict()

        user = self.user.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "event_id": event_id,
                "user_id": user_id,
                "event": event,
                "user": user,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_event_history_response_item import GetEventHistoryResponseItem
        from ..models.user import User

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        event_id = UUID(d.pop("event_id"))

        user_id = UUID(d.pop("user_id"))

        event = GetEventHistoryResponseItem.from_dict(d.pop("event"))

        user = User.from_dict(d.pop("user"))

        get_user_notifications_response_item = cls(
            id=id,
            event_id=event_id,
            user_id=user_id,
            event=event,
            user=user,
        )

        get_user_notifications_response_item.additional_properties = d
        return get_user_notifications_response_item

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
