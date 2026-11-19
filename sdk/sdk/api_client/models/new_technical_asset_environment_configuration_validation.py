from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.technical_mapping import TechnicalMapping
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.new_technical_asset_environment_configuration_validation_configuration import (
        NewTechnicalAssetEnvironmentConfigurationValidationConfiguration,
    )
    from ..models.new_technical_asset_environment_configuration_validation_environment_values import (
        NewTechnicalAssetEnvironmentConfigurationValidationEnvironmentValues,
    )


T = TypeVar("T", bound="NewTechnicalAssetEnvironmentConfigurationValidation")


@_attrs_define
class NewTechnicalAssetEnvironmentConfigurationValidation:
    """
    Attributes:
        namespace (str):
        configuration (NewTechnicalAssetEnvironmentConfigurationValidationConfiguration): Configuration of the technical
            asset. The available fields depend on `name`; retrieve them from /v2/plugins/{name}/form.
        technical_mapping (TechnicalMapping | Unset):
        environment_values (NewTechnicalAssetEnvironmentConfigurationValidationEnvironmentValues | Unset):
    """

    namespace: str
    configuration: NewTechnicalAssetEnvironmentConfigurationValidationConfiguration
    technical_mapping: TechnicalMapping | Unset = UNSET
    environment_values: (
        NewTechnicalAssetEnvironmentConfigurationValidationEnvironmentValues | Unset
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        namespace = self.namespace

        configuration = self.configuration.to_dict()

        technical_mapping: str | Unset = UNSET
        if not isinstance(self.technical_mapping, Unset):
            technical_mapping = self.technical_mapping.value

        environment_values: dict[str, Any] | Unset = UNSET
        if not isinstance(self.environment_values, Unset):
            environment_values = self.environment_values.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "namespace": namespace,
                "configuration": configuration,
            }
        )
        if technical_mapping is not UNSET:
            field_dict["technical_mapping"] = technical_mapping
        if environment_values is not UNSET:
            field_dict["environment_values"] = environment_values

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.new_technical_asset_environment_configuration_validation_configuration import (
            NewTechnicalAssetEnvironmentConfigurationValidationConfiguration,  # noqa: PLC0415
        )
        from ..models.new_technical_asset_environment_configuration_validation_environment_values import (
            NewTechnicalAssetEnvironmentConfigurationValidationEnvironmentValues,  # noqa: PLC0415
        )

        d = dict(src_dict)
        namespace = d.pop("namespace")

        configuration = (
            NewTechnicalAssetEnvironmentConfigurationValidationConfiguration.from_dict(
                d.pop("configuration")
            )
        )

        _technical_mapping = d.pop("technical_mapping", UNSET)
        technical_mapping: TechnicalMapping | Unset
        if isinstance(_technical_mapping, Unset):
            technical_mapping = UNSET
        else:
            technical_mapping = TechnicalMapping(_technical_mapping)

        _environment_values = d.pop("environment_values", UNSET)
        environment_values: (
            NewTechnicalAssetEnvironmentConfigurationValidationEnvironmentValues | Unset
        )
        if isinstance(_environment_values, Unset):
            environment_values = UNSET
        else:
            environment_values = NewTechnicalAssetEnvironmentConfigurationValidationEnvironmentValues.from_dict(
                _environment_values
            )

        new_technical_asset_environment_configuration_validation = cls(
            namespace=namespace,
            configuration=configuration,
            technical_mapping=technical_mapping,
            environment_values=environment_values,
        )

        new_technical_asset_environment_configuration_validation.additional_properties = d
        return new_technical_asset_environment_configuration_validation

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
