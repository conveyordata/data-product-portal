from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.environment_configuration_property import (
        EnvironmentConfigurationProperty,
    )


T = TypeVar("T", bound="GetTechnicalAssetEnvironmentConfigurationResponse")


@_attrs_define
class GetTechnicalAssetEnvironmentConfigurationResponse:
    """
    Attributes:
        properties (list[EnvironmentConfigurationProperty]):
    """

    properties: list[EnvironmentConfigurationProperty]
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
        from ..models.environment_configuration_property import (
            EnvironmentConfigurationProperty,  # noqa: PLC0415
        )

        d = dict(src_dict)
        properties = []
        _properties = d.pop("properties")
        for properties_item_data in _properties:
            properties_item = EnvironmentConfigurationProperty.from_dict(
                properties_item_data
            )

            properties.append(properties_item)

        get_technical_asset_environment_configuration_response = cls(
            properties=properties,
        )

        get_technical_asset_environment_configuration_response.additional_properties = d
        return get_technical_asset_environment_configuration_response

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
