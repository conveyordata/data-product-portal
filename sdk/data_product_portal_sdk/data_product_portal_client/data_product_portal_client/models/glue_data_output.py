from typing import Any, Literal, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GlueDataOutput")


@_attrs_define
class GlueDataOutput:
    """
    Attributes:
        configuration_type (Literal['GlueDataOutput']):
        database (str):
        database_suffix (Union[Unset, str]):  Default: ''.
        table (Union[Unset, str]):  Default: '*'.
        bucket_identifier (Union[Unset, str]):  Default: ''.
        database_path (Union[Unset, str]):  Default: ''.
        table_path (Union[Unset, str]):  Default: ''.
    """

    configuration_type: Literal["GlueDataOutput"]
    database: str
    database_suffix: Union[Unset, str] = ""
    table: Union[Unset, str] = "*"
    bucket_identifier: Union[Unset, str] = ""
    database_path: Union[Unset, str] = ""
    table_path: Union[Unset, str] = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        configuration_type = self.configuration_type

        database = self.database

        database_suffix = self.database_suffix

        table = self.table

        bucket_identifier = self.bucket_identifier

        database_path = self.database_path

        table_path = self.table_path

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "configuration_type": configuration_type,
                "database": database,
            }
        )
        if database_suffix is not UNSET:
            field_dict["database_suffix"] = database_suffix
        if table is not UNSET:
            field_dict["table"] = table
        if bucket_identifier is not UNSET:
            field_dict["bucket_identifier"] = bucket_identifier
        if database_path is not UNSET:
            field_dict["database_path"] = database_path
        if table_path is not UNSET:
            field_dict["table_path"] = table_path

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        configuration_type = cast(
            Literal["GlueDataOutput"], d.pop("configuration_type")
        )
        if configuration_type != "GlueDataOutput":
            raise ValueError(
                f"configuration_type must match const 'GlueDataOutput', got '{configuration_type}'"
            )

        database = d.pop("database")

        database_suffix = d.pop("database_suffix", UNSET)

        table = d.pop("table", UNSET)

        bucket_identifier = d.pop("bucket_identifier", UNSET)

        database_path = d.pop("database_path", UNSET)

        table_path = d.pop("table_path", UNSET)

        glue_data_output = cls(
            configuration_type=configuration_type,
            database=database,
            database_suffix=database_suffix,
            table=table,
            bucket_identifier=bucket_identifier,
            database_path=database_path,
            table_path=table_path,
        )

        glue_data_output.additional_properties = d
        return glue_data_output

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
