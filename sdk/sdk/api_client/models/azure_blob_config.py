from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.azure_blob_config_storage_account_names import (
        AzureBlobConfigStorageAccountNames,
    )


T = TypeVar("T", bound="AzureBlobConfig")


@_attrs_define
class AzureBlobConfig:
    """
    Attributes:
        identifier (str):
        storage_account_names (AzureBlobConfigStorageAccountNames):
    """

    identifier: str
    storage_account_names: AzureBlobConfigStorageAccountNames
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        identifier = self.identifier

        storage_account_names = self.storage_account_names.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "identifier": identifier,
                "storage_account_names": storage_account_names,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.azure_blob_config_storage_account_names import (
            AzureBlobConfigStorageAccountNames,
        )

        d = dict(src_dict)
        identifier = d.pop("identifier")

        storage_account_names = AzureBlobConfigStorageAccountNames.from_dict(
            d.pop("storage_account_names")
        )

        azure_blob_config = cls(
            identifier=identifier,
            storage_account_names=storage_account_names,
        )

        azure_blob_config.additional_properties = d
        return azure_blob_config

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
