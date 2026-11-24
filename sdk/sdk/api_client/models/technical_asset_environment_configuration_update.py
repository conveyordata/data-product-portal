from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.technical_asset_environment_configuration_update_environment_values import (
        TechnicalAssetEnvironmentConfigurationUpdateEnvironmentValues,
    )


T = TypeVar("T", bound="TechnicalAssetEnvironmentConfigurationUpdate")


@_attrs_define
class TechnicalAssetEnvironmentConfigurationUpdate:
    """
    Attributes:
        environment_values (TechnicalAssetEnvironmentConfigurationUpdateEnvironmentValues):
    """

    environment_values: TechnicalAssetEnvironmentConfigurationUpdateEnvironmentValues
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        environment_values = self.environment_values.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "environment_values": environment_values,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.technical_asset_environment_configuration_update_environment_values import (
            TechnicalAssetEnvironmentConfigurationUpdateEnvironmentValues,  # noqa: PLC0415
        )

        d = dict(src_dict)
        environment_values = (
            TechnicalAssetEnvironmentConfigurationUpdateEnvironmentValues.from_dict(
                d.pop("environment_values")
            )
        )

        technical_asset_environment_configuration_update = cls(
            environment_values=environment_values,
        )

        technical_asset_environment_configuration_update.additional_properties = d
        return technical_asset_environment_configuration_update

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
