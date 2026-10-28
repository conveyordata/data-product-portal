from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.identity_type import IdentityType

T = TypeVar("T", bound="GroupMemberIdentityGet")


@_attrs_define
class GroupMemberIdentityGet:
    """
    Attributes:
        id (UUID):
        type_ (IdentityType):
        external_id (str):
    """

    id: UUID
    type_: IdentityType
    external_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        type_ = self.type_.value

        external_id = self.external_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "type": type_,
                "external_id": external_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        type_ = IdentityType(d.pop("type"))

        external_id = d.pop("external_id")

        group_member_identity_get = cls(
            id=id,
            type_=type_,
            external_id=external_id,
        )

        group_member_identity_get.additional_properties = d
        return group_member_identity_get

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
