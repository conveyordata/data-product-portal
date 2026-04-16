from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AzureEnvironmentPlatformConfiguration")


@_attrs_define
class AzureEnvironmentPlatformConfiguration:
    """
    Attributes:
        tenant_id (str):
        subscription_id (str):
        region (str):
    """

    tenant_id: str
    subscription_id: str
    region: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tenant_id = self.tenant_id

        subscription_id = self.subscription_id

        region = self.region

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tenant_id": tenant_id,
                "subscription_id": subscription_id,
                "region": region,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tenant_id = d.pop("tenant_id")

        subscription_id = d.pop("subscription_id")

        region = d.pop("region")

        azure_environment_platform_configuration = cls(
            tenant_id=tenant_id,
            subscription_id=subscription_id,
            region=region,
        )

        azure_environment_platform_configuration.additional_properties = d
        return azure_environment_platform_configuration

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
