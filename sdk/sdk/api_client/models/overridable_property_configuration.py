from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.environment_property_value import EnvironmentPropertyValue


T = TypeVar("T", bound="OverridablePropertyConfiguration")


@_attrs_define
class OverridablePropertyConfiguration:
    """
    Attributes:
        name (str):
        label (str):
        allowed_values (list[str]):
        default (str):
        base_value (str):
        environments (list[EnvironmentPropertyValue]):
    """

    name: str
    label: str
    allowed_values: list[str]
    default: str
    base_value: str
    environments: list[EnvironmentPropertyValue]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        label = self.label

        allowed_values = self.allowed_values

        default = self.default

        base_value = self.base_value

        environments = []
        for environments_item_data in self.environments:
            environments_item = environments_item_data.to_dict()
            environments.append(environments_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "label": label,
                "allowed_values": allowed_values,
                "default": default,
                "base_value": base_value,
                "environments": environments,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.environment_property_value import (
            EnvironmentPropertyValue,  # noqa: PLC0415
        )

        d = dict(src_dict)
        name = d.pop("name")

        label = d.pop("label")

        allowed_values = cast(list[str], d.pop("allowed_values"))

        default = d.pop("default")

        base_value = d.pop("base_value")

        environments = []
        _environments = d.pop("environments")
        for environments_item_data in _environments:
            environments_item = EnvironmentPropertyValue.from_dict(
                environments_item_data
            )

            environments.append(environments_item)

        overridable_property_configuration = cls(
            name=name,
            label=label,
            allowed_values=allowed_values,
            default=default,
            base_value=base_value,
            environments=environments,
        )

        overridable_property_configuration.additional_properties = d
        return overridable_property_configuration

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
