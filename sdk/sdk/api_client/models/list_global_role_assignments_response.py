from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.global_role_assignment_response import GlobalRoleAssignmentResponse


T = TypeVar("T", bound="ListGlobalRoleAssignmentsResponse")


@_attrs_define
class ListGlobalRoleAssignmentsResponse:
    """
    Attributes:
        role_assignments (list[GlobalRoleAssignmentResponse]):
    """

    role_assignments: list[GlobalRoleAssignmentResponse]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        role_assignments = []
        for role_assignments_item_data in self.role_assignments:
            role_assignments_item = role_assignments_item_data.to_dict()
            role_assignments.append(role_assignments_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "role_assignments": role_assignments,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.global_role_assignment_response import (
            GlobalRoleAssignmentResponse,
        )

        d = dict(src_dict)
        role_assignments = []
        _role_assignments = d.pop("role_assignments")
        for role_assignments_item_data in _role_assignments:
            role_assignments_item = GlobalRoleAssignmentResponse.from_dict(
                role_assignments_item_data
            )

            role_assignments.append(role_assignments_item)

        list_global_role_assignments_response = cls(
            role_assignments=role_assignments,
        )

        list_global_role_assignments_response.additional_properties = d
        return list_global_role_assignments_response

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
