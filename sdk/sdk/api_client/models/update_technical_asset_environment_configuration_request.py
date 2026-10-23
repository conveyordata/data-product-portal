from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.update_technical_asset_environment_configuration_request_base_values import (
        UpdateTechnicalAssetEnvironmentConfigurationRequestBaseValues,
    )
    from ..models.update_technical_asset_environment_configuration_request_overrides import (
        UpdateTechnicalAssetEnvironmentConfigurationRequestOverrides,
    )


T = TypeVar("T", bound="UpdateTechnicalAssetEnvironmentConfigurationRequest")


@_attrs_define
class UpdateTechnicalAssetEnvironmentConfigurationRequest:
    """
    Attributes:
        base_values (UpdateTechnicalAssetEnvironmentConfigurationRequestBaseValues):
        overrides (UpdateTechnicalAssetEnvironmentConfigurationRequestOverrides):
    """

    base_values: UpdateTechnicalAssetEnvironmentConfigurationRequestBaseValues
    overrides: UpdateTechnicalAssetEnvironmentConfigurationRequestOverrides
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        base_values = self.base_values.to_dict()

        overrides = self.overrides.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "base_values": base_values,
                "overrides": overrides,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_technical_asset_environment_configuration_request_base_values import (
            UpdateTechnicalAssetEnvironmentConfigurationRequestBaseValues,  # noqa: PLC0415
        )
        from ..models.update_technical_asset_environment_configuration_request_overrides import (
            UpdateTechnicalAssetEnvironmentConfigurationRequestOverrides,  # noqa: PLC0415
        )

        d = dict(src_dict)
        base_values = (
            UpdateTechnicalAssetEnvironmentConfigurationRequestBaseValues.from_dict(
                d.pop("base_values")
            )
        )

        overrides = (
            UpdateTechnicalAssetEnvironmentConfigurationRequestOverrides.from_dict(
                d.pop("overrides")
            )
        )

        update_technical_asset_environment_configuration_request = cls(
            base_values=base_values,
            overrides=overrides,
        )

        update_technical_asset_environment_configuration_request.additional_properties = d
        return update_technical_asset_environment_configuration_request

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
