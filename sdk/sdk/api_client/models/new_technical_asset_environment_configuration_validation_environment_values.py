from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.new_technical_asset_environment_configuration_validation_environment_values_additional_property import (
        NewTechnicalAssetEnvironmentConfigurationValidationEnvironmentValuesAdditionalProperty,
    )


T = TypeVar(
    "T", bound="NewTechnicalAssetEnvironmentConfigurationValidationEnvironmentValues"
)


@_attrs_define
class NewTechnicalAssetEnvironmentConfigurationValidationEnvironmentValues:
    additional_properties: dict[
        str,
        NewTechnicalAssetEnvironmentConfigurationValidationEnvironmentValuesAdditionalProperty,
    ] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.new_technical_asset_environment_configuration_validation_environment_values_additional_property import (
            NewTechnicalAssetEnvironmentConfigurationValidationEnvironmentValuesAdditionalProperty,  # noqa: PLC0415
        )

        d = dict(src_dict)
        new_technical_asset_environment_configuration_validation_environment_values = (
            cls()
        )

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = NewTechnicalAssetEnvironmentConfigurationValidationEnvironmentValuesAdditionalProperty.from_dict(
                prop_dict
            )

            additional_properties[prop_name] = additional_property

        new_technical_asset_environment_configuration_validation_environment_values.additional_properties = additional_properties
        return (
            new_technical_asset_environment_configuration_validation_environment_values
        )

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(
        self, key: str
    ) -> NewTechnicalAssetEnvironmentConfigurationValidationEnvironmentValuesAdditionalProperty:
        return self.additional_properties[key]

    def __setitem__(
        self,
        key: str,
        value: NewTechnicalAssetEnvironmentConfigurationValidationEnvironmentValuesAdditionalProperty,
    ) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
