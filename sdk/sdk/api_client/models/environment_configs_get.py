from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.environment_configs_get_item import EnvironmentConfigsGetItem


T = TypeVar("T", bound="EnvironmentConfigsGet")


@_attrs_define
class EnvironmentConfigsGet:
    """
    Attributes:
        environment_configs (list[EnvironmentConfigsGetItem]):
    """

    environment_configs: list[EnvironmentConfigsGetItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        environment_configs = []
        for environment_configs_item_data in self.environment_configs:
            environment_configs_item = environment_configs_item_data.to_dict()
            environment_configs.append(environment_configs_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "environment_configs": environment_configs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.environment_configs_get_item import EnvironmentConfigsGetItem

        d = dict(src_dict)
        environment_configs = []
        _environment_configs = d.pop("environment_configs")
        for environment_configs_item_data in _environment_configs:
            environment_configs_item = EnvironmentConfigsGetItem.from_dict(
                environment_configs_item_data
            )

            environment_configs.append(environment_configs_item)

        environment_configs_get = cls(
            environment_configs=environment_configs,
        )

        environment_configs_get.additional_properties = d
        return environment_configs_get

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
