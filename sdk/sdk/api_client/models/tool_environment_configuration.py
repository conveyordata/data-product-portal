from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.overridable_property_configuration import (
        OverridablePropertyConfiguration,
    )


T = TypeVar("T", bound="ToolEnvironmentConfiguration")


@_attrs_define
class ToolEnvironmentConfiguration:
    """
    Attributes:
        properties (list[OverridablePropertyConfiguration]):
    """

    properties: list[OverridablePropertyConfiguration]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        properties = []
        for properties_item_data in self.properties:
            properties_item = properties_item_data.to_dict()
            properties.append(properties_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "properties": properties,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.overridable_property_configuration import (
            OverridablePropertyConfiguration,  # noqa: PLC0415
        )

        d = dict(src_dict)
        properties = []
        _properties = d.pop("properties")
        for properties_item_data in _properties:
            properties_item = OverridablePropertyConfiguration.from_dict(
                properties_item_data
            )

            properties.append(properties_item)

        tool_environment_configuration = cls(
            properties=properties,
        )

        tool_environment_configuration.additional_properties = d
        return tool_environment_configuration

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
