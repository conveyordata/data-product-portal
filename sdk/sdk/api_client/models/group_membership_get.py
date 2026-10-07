from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.group_member_identity_get import GroupMemberIdentityGet


T = TypeVar("T", bound="GroupMembershipGet")


@_attrs_define
class GroupMembershipGet:
    """
    Attributes:
        group_id (UUID):
        member_identity_id (UUID):
        member (GroupMemberIdentityGet):
    """

    group_id: UUID
    member_identity_id: UUID
    member: GroupMemberIdentityGet
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        group_id = str(self.group_id)

        member_identity_id = str(self.member_identity_id)

        member = self.member.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "group_id": group_id,
                "member_identity_id": member_identity_id,
                "member": member,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.group_member_identity_get import GroupMemberIdentityGet

        d = dict(src_dict)
        group_id = UUID(d.pop("group_id"))

        member_identity_id = UUID(d.pop("member_identity_id"))

        member = GroupMemberIdentityGet.from_dict(d.pop("member"))

        group_membership_get = cls(
            group_id=group_id,
            member_identity_id=member_identity_id,
            member=member,
        )

        group_membership_get.additional_properties = d
        return group_membership_get

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
