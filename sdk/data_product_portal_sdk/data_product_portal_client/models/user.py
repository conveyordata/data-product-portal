from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """
    Attributes:
        email (str):
        external_id (str):
        first_name (str):
        last_name (str):
        is_admin (bool):
        id (UUID):
    """

    email: str
    external_id: str
    first_name: str
    last_name: str
    is_admin: bool
    id: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        external_id = self.external_id

        first_name = self.first_name

        last_name = self.last_name

        is_admin = self.is_admin

        id = str(self.id)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "external_id": external_id,
                "first_name": first_name,
                "last_name": last_name,
                "is_admin": is_admin,
                "id": id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        email = d.pop("email")

        external_id = d.pop("external_id")

        first_name = d.pop("first_name")

        last_name = d.pop("last_name")

        is_admin = d.pop("is_admin")

        id = UUID(d.pop("id"))

        user = cls(
            email=email,
            external_id=external_id,
            first_name=first_name,
            last_name=last_name,
            is_admin=is_admin,
            id=id,
        )

        user.additional_properties = d
        return user

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
