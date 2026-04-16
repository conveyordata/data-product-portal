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

from ..models.access_granularity import AccessGranularity
from ..types import UNSET, Unset

T = TypeVar("T", bound="DatabricksTechnicalAssetConfiguration")


@_attrs_define
class DatabricksTechnicalAssetConfiguration:
    """
    Attributes:
        configuration_type (Literal['DatabricksTechnicalAssetConfiguration']):
        catalog (str):
        access_granularity (AccessGranularity):
        schema (str | Unset):  Default: ''.
        table (str | Unset):  Default: '*'.
        bucket_identifier (str | Unset):  Default: ''.
        catalog_path (str | Unset):  Default: ''.
        table_path (str | Unset):  Default: ''.
    """

    configuration_type: Literal["DatabricksTechnicalAssetConfiguration"]
    catalog: str
    access_granularity: AccessGranularity
    schema: str | Unset = ""
    table: str | Unset = "*"
    bucket_identifier: str | Unset = ""
    catalog_path: str | Unset = ""
    table_path: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        configuration_type = self.configuration_type

        catalog = self.catalog

        access_granularity = self.access_granularity.value

        schema = self.schema

        table = self.table

        bucket_identifier = self.bucket_identifier

        catalog_path = self.catalog_path

        table_path = self.table_path

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "configuration_type": configuration_type,
                "catalog": catalog,
                "access_granularity": access_granularity,
            }
        )
        if schema is not UNSET:
            field_dict["schema"] = schema
        if table is not UNSET:
            field_dict["table"] = table
        if bucket_identifier is not UNSET:
            field_dict["bucket_identifier"] = bucket_identifier
        if catalog_path is not UNSET:
            field_dict["catalog_path"] = catalog_path
        if table_path is not UNSET:
            field_dict["table_path"] = table_path

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        configuration_type = cast(
            Literal["DatabricksTechnicalAssetConfiguration"],
            d.pop("configuration_type"),
        )
        if configuration_type != "DatabricksTechnicalAssetConfiguration":
            raise ValueError(
                f"configuration_type must match const 'DatabricksTechnicalAssetConfiguration', got '{configuration_type}'"
            )

        catalog = d.pop("catalog")

        access_granularity = AccessGranularity(d.pop("access_granularity"))

        schema = d.pop("schema", UNSET)

        table = d.pop("table", UNSET)

        bucket_identifier = d.pop("bucket_identifier", UNSET)

        catalog_path = d.pop("catalog_path", UNSET)

        table_path = d.pop("table_path", UNSET)

        databricks_technical_asset_configuration = cls(
            configuration_type=configuration_type,
            catalog=catalog,
            access_granularity=access_granularity,
            schema=schema,
            table=table,
            bucket_identifier=bucket_identifier,
            catalog_path=catalog_path,
            table_path=table_path,
        )

        databricks_technical_asset_configuration.additional_properties = d
        return databricks_technical_asset_configuration

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
