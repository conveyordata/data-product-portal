from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GroupMembersReplace")


@_attrs_define
class GroupMembersReplace:
    """
    Attributes:
        member_identity_ids (list[UUID]):
    """

    member_identity_ids: list[UUID]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        member_identity_ids = []
        for member_identity_ids_item_data in self.member_identity_ids:
            member_identity_ids_item = str(member_identity_ids_item_data)
            member_identity_ids.append(member_identity_ids_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "member_identity_ids": member_identity_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        member_identity_ids = []
        _member_identity_ids = d.pop("member_identity_ids")
        for member_identity_ids_item_data in _member_identity_ids:
            member_identity_ids_item = UUID(member_identity_ids_item_data)

            member_identity_ids.append(member_identity_ids_item)

        group_members_replace = cls(
            member_identity_ids=member_identity_ids,
        )

        group_members_replace.additional_properties = d
        return group_members_replace

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
