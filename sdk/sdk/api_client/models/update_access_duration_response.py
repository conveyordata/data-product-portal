from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.access_duration import AccessDuration


T = TypeVar("T", bound="UpdateAccessDurationResponse")


@_attrs_define
class UpdateAccessDurationResponse:
    """
    Attributes:
        access_durations (list[AccessDuration]):
    """

    access_durations: list[AccessDuration]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access_durations = []
        for access_durations_item_data in self.access_durations:
            access_durations_item = access_durations_item_data.to_dict()
            access_durations.append(access_durations_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "access_durations": access_durations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_duration import AccessDuration

        d = dict(src_dict)
        access_durations = []
        _access_durations = d.pop("access_durations")
        for access_durations_item_data in _access_durations:
            access_durations_item = AccessDuration.from_dict(access_durations_item_data)

            access_durations.append(access_durations_item)

        update_access_duration_response = cls(
            access_durations=access_durations,
        )

        update_access_duration_response.additional_properties = d
        return update_access_duration_response

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
