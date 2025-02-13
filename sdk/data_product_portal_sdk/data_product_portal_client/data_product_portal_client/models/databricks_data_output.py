from typing import Any, Literal, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DatabricksDataOutput")


@_attrs_define
class DatabricksDataOutput:
    """
    Attributes:
        configuration_type (Literal['DatabricksDataOutput']):
        catalog (str):
        schema (Union[Unset, str]):  Default: ''.
        table (Union[Unset, str]):  Default: '*'.
        bucket_identifier (Union[Unset, str]):  Default: ''.
        catalog_path (Union[Unset, str]):  Default: ''.
        table_path (Union[Unset, str]):  Default: ''.
    """

    configuration_type: Literal["DatabricksDataOutput"]
    catalog: str
    schema: Union[Unset, str] = ""
    table: Union[Unset, str] = "*"
    bucket_identifier: Union[Unset, str] = ""
    catalog_path: Union[Unset, str] = ""
    table_path: Union[Unset, str] = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        configuration_type = self.configuration_type

        catalog = self.catalog

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
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        configuration_type = cast(
            Literal["DatabricksDataOutput"], d.pop("configuration_type")
        )
        if configuration_type != "DatabricksDataOutput":
            raise ValueError(
                f"configuration_type must match const 'DatabricksDataOutput', got '{configuration_type}'"
            )

        catalog = d.pop("catalog")

        schema = d.pop("schema", UNSET)

        table = d.pop("table", UNSET)

        bucket_identifier = d.pop("bucket_identifier", UNSET)

        catalog_path = d.pop("catalog_path", UNSET)

        table_path = d.pop("table_path", UNSET)

        databricks_data_output = cls(
            configuration_type=configuration_type,
            catalog=catalog,
            schema=schema,
            table=table,
            bucket_identifier=bucket_identifier,
            catalog_path=catalog_path,
            table_path=table_path,
        )

        databricks_data_output.additional_properties = d
        return databricks_data_output

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
