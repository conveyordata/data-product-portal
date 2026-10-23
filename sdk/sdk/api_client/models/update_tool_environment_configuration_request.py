from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_tool_environment_configuration_request_base_values import (
        UpdateToolEnvironmentConfigurationRequestBaseValues,
    )
    from ..models.update_tool_environment_configuration_request_overrides import (
        UpdateToolEnvironmentConfigurationRequestOverrides,
    )


T = TypeVar("T", bound="UpdateToolEnvironmentConfigurationRequest")


@_attrs_define
class UpdateToolEnvironmentConfigurationRequest:
    """
    Attributes:
        base_values (UpdateToolEnvironmentConfigurationRequestBaseValues | Unset):
        overrides (UpdateToolEnvironmentConfigurationRequestOverrides | Unset):
    """

    base_values: UpdateToolEnvironmentConfigurationRequestBaseValues | Unset = UNSET
    overrides: UpdateToolEnvironmentConfigurationRequestOverrides | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        base_values: dict[str, Any] | Unset = UNSET
        if not isinstance(self.base_values, Unset):
            base_values = self.base_values.to_dict()

        overrides: dict[str, Any] | Unset = UNSET
        if not isinstance(self.overrides, Unset):
            overrides = self.overrides.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if base_values is not UNSET:
            field_dict["base_values"] = base_values
        if overrides is not UNSET:
            field_dict["overrides"] = overrides

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_tool_environment_configuration_request_base_values import (
            UpdateToolEnvironmentConfigurationRequestBaseValues,  # noqa: PLC0415
        )
        from ..models.update_tool_environment_configuration_request_overrides import (
            UpdateToolEnvironmentConfigurationRequestOverrides,  # noqa: PLC0415
        )

        d = dict(src_dict)
        _base_values = d.pop("base_values", UNSET)
        base_values: UpdateToolEnvironmentConfigurationRequestBaseValues | Unset
        if isinstance(_base_values, Unset):
            base_values = UNSET
        else:
            base_values = UpdateToolEnvironmentConfigurationRequestBaseValues.from_dict(
                _base_values
            )

        _overrides = d.pop("overrides", UNSET)
        overrides: UpdateToolEnvironmentConfigurationRequestOverrides | Unset
        if isinstance(_overrides, Unset):
            overrides = UNSET
        else:
            overrides = UpdateToolEnvironmentConfigurationRequestOverrides.from_dict(
                _overrides
            )

        update_tool_environment_configuration_request = cls(
            base_values=base_values,
            overrides=overrides,
        )

        update_tool_environment_configuration_request.additional_properties = d
        return update_tool_environment_configuration_request

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
