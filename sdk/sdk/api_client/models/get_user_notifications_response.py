from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_user_notifications_response_item import (
        GetUserNotificationsResponseItem,
    )


T = TypeVar("T", bound="GetUserNotificationsResponse")


@_attrs_define
class GetUserNotificationsResponse:
    """
    Attributes:
        notifications (list[GetUserNotificationsResponseItem]):
    """

    notifications: list[GetUserNotificationsResponseItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        notifications = []
        for notifications_item_data in self.notifications:
            notifications_item = notifications_item_data.to_dict()
            notifications.append(notifications_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "notifications": notifications,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_user_notifications_response_item import (
            GetUserNotificationsResponseItem,
        )

        d = dict(src_dict)
        notifications = []
        _notifications = d.pop("notifications")
        for notifications_item_data in _notifications:
            notifications_item = GetUserNotificationsResponseItem.from_dict(
                notifications_item_data
            )

            notifications.append(notifications_item)

        get_user_notifications_response = cls(
            notifications=notifications,
        )

        get_user_notifications_response.additional_properties = d
        return get_user_notifications_response

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
