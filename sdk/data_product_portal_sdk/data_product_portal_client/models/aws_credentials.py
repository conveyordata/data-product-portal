import datetime
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="AWSCredentials")


@_attrs_define
class AWSCredentials:
    """
    Attributes:
        access_key_id (str):
        secret_access_key (str):
        session_token (str):
        expiration (datetime.datetime):
    """

    access_key_id: str
    secret_access_key: str
    session_token: str
    expiration: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access_key_id = self.access_key_id

        secret_access_key = self.secret_access_key

        session_token = self.session_token

        expiration = self.expiration.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "AccessKeyId": access_key_id,
                "SecretAccessKey": secret_access_key,
                "SessionToken": session_token,
                "Expiration": expiration,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        access_key_id = d.pop("AccessKeyId")

        secret_access_key = d.pop("SecretAccessKey")

        session_token = d.pop("SessionToken")

        expiration = isoparse(d.pop("Expiration"))

        aws_credentials = cls(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            session_token=session_token,
            expiration=expiration,
        )

        aws_credentials.additional_properties = d
        return aws_credentials

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
