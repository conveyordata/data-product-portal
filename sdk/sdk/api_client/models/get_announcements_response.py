from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.announcement import Announcement


T = TypeVar("T", bound="GetAnnouncementsResponse")


@_attrs_define
class GetAnnouncementsResponse:
    """
    Attributes:
        announcements (list[Announcement]):
    """

    announcements: list[Announcement]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        announcements = []
        for announcements_item_data in self.announcements:
            announcements_item = announcements_item_data.to_dict()
            announcements.append(announcements_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "announcements": announcements,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.announcement import Announcement  # noqa: PLC0415

        d = dict(src_dict)
        announcements = []
        _announcements = d.pop("announcements")
        for announcements_item_data in _announcements:
            announcements_item = Announcement.from_dict(announcements_item_data)

            announcements.append(announcements_item)

        get_announcements_response = cls(
            announcements=announcements,
        )

        get_announcements_response.additional_properties = d
        return get_announcements_response

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
