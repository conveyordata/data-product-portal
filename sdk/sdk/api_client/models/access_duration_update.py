from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.access_duration_type import AccessDurationType
from ..types import UNSET, Unset

T = TypeVar("T", bound="AccessDurationUpdate")


@_attrs_define
class AccessDurationUpdate:
    """
    Attributes:
        access_duration_type (AccessDurationType):
        alternative_allowed (bool):
        days (int | None | Unset):
        alternative_days (int | None | Unset):
    """

    access_duration_type: AccessDurationType
    alternative_allowed: bool
    days: int | None | Unset = UNSET
    alternative_days: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access_duration_type = self.access_duration_type.value

        alternative_allowed = self.alternative_allowed

        days: int | None | Unset
        if isinstance(self.days, Unset):
            days = UNSET
        else:
            days = self.days

        alternative_days: int | None | Unset
        if isinstance(self.alternative_days, Unset):
            alternative_days = UNSET
        else:
            alternative_days = self.alternative_days

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "access_duration_type": access_duration_type,
                "alternative_allowed": alternative_allowed,
            }
        )
        if days is not UNSET:
            field_dict["days"] = days
        if alternative_days is not UNSET:
            field_dict["alternative_days"] = alternative_days

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        access_duration_type = AccessDurationType(d.pop("access_duration_type"))

        alternative_allowed = d.pop("alternative_allowed")

        def _parse_days(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        days = _parse_days(d.pop("days", UNSET))

        def _parse_alternative_days(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        alternative_days = _parse_alternative_days(d.pop("alternative_days", UNSET))

        access_duration_update = cls(
            access_duration_type=access_duration_type,
            alternative_allowed=alternative_allowed,
            days=days,
            alternative_days=alternative_days,
        )

        access_duration_update.additional_properties = d
        return access_duration_update

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
