from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AWSGlueConfig")


@_attrs_define
class AWSGlueConfig:
    """
    Attributes:
        identifier (str):
        database_name (str):
        bucket_identifier (str):
        s3_path (str):
    """

    identifier: str
    database_name: str
    bucket_identifier: str
    s3_path: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        identifier = self.identifier

        database_name = self.database_name

        bucket_identifier = self.bucket_identifier

        s3_path = self.s3_path

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "identifier": identifier,
                "database_name": database_name,
                "bucket_identifier": bucket_identifier,
                "s3_path": s3_path,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        identifier = d.pop("identifier")

        database_name = d.pop("database_name")

        bucket_identifier = d.pop("bucket_identifier")

        s3_path = d.pop("s3_path")

        aws_glue_config = cls(
            identifier=identifier,
            database_name=database_name,
            bucket_identifier=bucket_identifier,
            s3_path=s3_path,
        )

        aws_glue_config.additional_properties = d
        return aws_glue_config

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
