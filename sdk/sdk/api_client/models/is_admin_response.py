from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="IsAdminResponse")


@_attrs_define
class IsAdminResponse:
    """
    Attributes:
        is_admin (bool):
        time (None | str | Unset):
    """

    is_admin: bool
    time: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_admin = self.is_admin

        time: None | str | Unset
        if isinstance(self.time, Unset):
            time = UNSET
        else:
            time = self.time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "is_admin": is_admin,
            }
        )
        if time is not UNSET:
            field_dict["time"] = time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_admin = d.pop("is_admin")

        def _parse_time(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        time = _parse_time(d.pop("time", UNSET))

        is_admin_response = cls(
            is_admin=is_admin,
            time=time,
        )

        is_admin_response.additional_properties = d
        return is_admin_response

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
