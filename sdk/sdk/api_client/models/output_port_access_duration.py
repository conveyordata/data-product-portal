from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.access_duration_type import AccessDurationType

T = TypeVar("T", bound="OutputPortAccessDuration")


@_attrs_define
class OutputPortAccessDuration:
    """
    Attributes:
        access_duration_type (AccessDurationType):
        days (int):
    """

    access_duration_type: AccessDurationType
    days: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access_duration_type = self.access_duration_type.value

        days = self.days

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "access_duration_type": access_duration_type,
                "days": days,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        access_duration_type = AccessDurationType(d.pop("access_duration_type"))

        days = d.pop("days")

        output_port_access_duration = cls(
            access_duration_type=access_duration_type,
            days=days,
        )

        output_port_access_duration.additional_properties = d
        return output_port_access_duration

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
