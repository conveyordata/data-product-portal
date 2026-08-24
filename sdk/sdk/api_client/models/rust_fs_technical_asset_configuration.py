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

T = TypeVar("T", bound="RustFSTechnicalAssetConfiguration")


@_attrs_define
class RustFSTechnicalAssetConfiguration:
    """
    Attributes:
        configuration_type (Literal['RustFSTechnicalAssetConfiguration']):
        bucket (str):
        path (str):
        suffix (str | Unset):  Default: ''.
    """

    configuration_type: Literal["RustFSTechnicalAssetConfiguration"]
    bucket: str
    path: str
    suffix: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        configuration_type = self.configuration_type

        bucket = self.bucket

        path = self.path

        suffix = self.suffix

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "configuration_type": configuration_type,
                "bucket": bucket,
                "path": path,
            }
        )
        if suffix is not UNSET:
            field_dict["suffix"] = suffix

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        configuration_type = cast(
            Literal["RustFSTechnicalAssetConfiguration"], d.pop("configuration_type")
        )
        if configuration_type != "RustFSTechnicalAssetConfiguration":
            raise ValueError(
                f"configuration_type must match const 'RustFSTechnicalAssetConfiguration', got '{configuration_type}'"
            )

        bucket = d.pop("bucket")

        path = d.pop("path")

        suffix = d.pop("suffix", UNSET)

        rust_fs_technical_asset_configuration = cls(
            configuration_type=configuration_type,
            bucket=bucket,
            path=path,
            suffix=suffix,
        )

        rust_fs_technical_asset_configuration.additional_properties = d
        return rust_fs_technical_asset_configuration

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
