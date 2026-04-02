from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.platform_service import PlatformService


T = TypeVar("T", bound="GetPlatformServicesResponse")


@_attrs_define
class GetPlatformServicesResponse:
    """
    Attributes:
        platform_services (list[PlatformService]):
    """

    platform_services: list[PlatformService]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        platform_services = []
        for platform_services_item_data in self.platform_services:
            platform_services_item = platform_services_item_data.to_dict()
            platform_services.append(platform_services_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "platform_services": platform_services,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.platform_service import PlatformService

        d = dict(src_dict)
        platform_services = []
        _platform_services = d.pop("platform_services")
        for platform_services_item_data in _platform_services:
            platform_services_item = PlatformService.from_dict(
                platform_services_item_data
            )

            platform_services.append(platform_services_item)

        get_platform_services_response = cls(
            platform_services=platform_services,
        )

        get_platform_services_response.additional_properties = d
        return get_platform_services_response

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
