from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="OverridableProperty")


@_attrs_define
class OverridableProperty:
    """
    Attributes:
        name (str):
        label (str):
        allowed_values (list[str]):
        default (str):
    """

    name: str
    label: str
    allowed_values: list[str]
    default: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        label = self.label

        allowed_values = self.allowed_values

        default = self.default

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "label": label,
                "allowed_values": allowed_values,
                "default": default,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        label = d.pop("label")

        allowed_values = cast(list[str], d.pop("allowed_values"))

        default = d.pop("default")

        overridable_property = cls(
            name=name,
            label=label,
            allowed_values=allowed_values,
            default=default,
        )

        overridable_property.additional_properties = d
        return overridable_property

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
