from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.platform_service_configuration import PlatformServiceConfiguration


T = TypeVar("T", bound="GetAllPlatformServiceConfigurationsResponse")


@_attrs_define
class GetAllPlatformServiceConfigurationsResponse:
    """
    Attributes:
        platform_service_configurations (list[PlatformServiceConfiguration]):
    """

    platform_service_configurations: list[PlatformServiceConfiguration]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        platform_service_configurations = []
        for (
            platform_service_configurations_item_data
        ) in self.platform_service_configurations:
            platform_service_configurations_item = (
                platform_service_configurations_item_data.to_dict()
            )
            platform_service_configurations.append(platform_service_configurations_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "platform_service_configurations": platform_service_configurations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.platform_service_configuration import PlatformServiceConfiguration

        d = dict(src_dict)
        platform_service_configurations = []
        _platform_service_configurations = d.pop("platform_service_configurations")
        for (
            platform_service_configurations_item_data
        ) in _platform_service_configurations:
            platform_service_configurations_item = (
                PlatformServiceConfiguration.from_dict(
                    platform_service_configurations_item_data
                )
            )

            platform_service_configurations.append(platform_service_configurations_item)

        get_all_platform_service_configurations_response = cls(
            platform_service_configurations=platform_service_configurations,
        )

        get_all_platform_service_configurations_response.additional_properties = d
        return get_all_platform_service_configurations_response

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
