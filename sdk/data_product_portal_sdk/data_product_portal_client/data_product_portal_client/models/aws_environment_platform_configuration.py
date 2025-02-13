from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AWSEnvironmentPlatformConfiguration")


@_attrs_define
class AWSEnvironmentPlatformConfiguration:
    """
    Attributes:
        account_id (str):
        region (str):
        can_read_from (list[str]):
    """

    account_id: str
    region: str
    can_read_from: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        account_id = self.account_id

        region = self.region

        can_read_from = self.can_read_from

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "account_id": account_id,
                "region": region,
                "can_read_from": can_read_from,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        account_id = d.pop("account_id")

        region = d.pop("region")

        can_read_from = cast(list[str], d.pop("can_read_from"))

        aws_environment_platform_configuration = cls(
            account_id=account_id,
            region=region,
            can_read_from=can_read_from,
        )

        aws_environment_platform_configuration.additional_properties = d
        return aws_environment_platform_configuration

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
