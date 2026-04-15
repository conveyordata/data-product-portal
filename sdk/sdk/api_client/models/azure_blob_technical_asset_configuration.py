from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AzureBlobTechnicalAssetConfiguration")


@_attrs_define
class AzureBlobTechnicalAssetConfiguration:
    """
    Attributes:
        configuration_type (Literal['AzureBlobTechnicalAssetConfiguration']):
        container_name (str):
        domain (str | Unset):  Default: ''.
        path (str | Unset):  Default: ''.
    """

    configuration_type: Literal["AzureBlobTechnicalAssetConfiguration"]
    container_name: str
    domain: str | Unset = ""
    path: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        configuration_type = self.configuration_type

        container_name = self.container_name

        domain = self.domain

        path = self.path

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "configuration_type": configuration_type,
                "container_name": container_name,
            }
        )
        if domain is not UNSET:
            field_dict["domain"] = domain
        if path is not UNSET:
            field_dict["path"] = path

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        configuration_type = cast(
            Literal["AzureBlobTechnicalAssetConfiguration"], d.pop("configuration_type")
        )
        if configuration_type != "AzureBlobTechnicalAssetConfiguration":
            raise ValueError(
                f"configuration_type must match const 'AzureBlobTechnicalAssetConfiguration', got '{configuration_type}'"
            )

        container_name = d.pop("container_name")

        domain = d.pop("domain", UNSET)

        path = d.pop("path", UNSET)

        azure_blob_technical_asset_configuration = cls(
            configuration_type=configuration_type,
            container_name=container_name,
            domain=domain,
            path=path,
        )

        azure_blob_technical_asset_configuration.additional_properties = d
        return azure_blob_technical_asset_configuration

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
