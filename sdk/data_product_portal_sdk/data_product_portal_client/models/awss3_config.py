from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AWSS3Config")


@_attrs_define
class AWSS3Config:
    """
    Attributes:
        identifier (str):
        bucket_name (str):
        bucket_arn (str):
        kms_key_arn (str):
        is_default (bool):
    """

    identifier: str
    bucket_name: str
    bucket_arn: str
    kms_key_arn: str
    is_default: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        identifier = self.identifier

        bucket_name = self.bucket_name

        bucket_arn = self.bucket_arn

        kms_key_arn = self.kms_key_arn

        is_default = self.is_default

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "identifier": identifier,
                "bucket_name": bucket_name,
                "bucket_arn": bucket_arn,
                "kms_key_arn": kms_key_arn,
                "is_default": is_default,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        identifier = d.pop("identifier")

        bucket_name = d.pop("bucket_name")

        bucket_arn = d.pop("bucket_arn")

        kms_key_arn = d.pop("kms_key_arn")

        is_default = d.pop("is_default")

        awss3_config = cls(
            identifier=identifier,
            bucket_name=bucket_name,
            bucket_arn=bucket_arn,
            kms_key_arn=kms_key_arn,
            is_default=is_default,
        )

        awss3_config.additional_properties = d
        return awss3_config

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
