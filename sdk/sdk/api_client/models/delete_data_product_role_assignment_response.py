from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DeleteDataProductRoleAssignmentResponse")


@_attrs_define
class DeleteDataProductRoleAssignmentResponse:
    """
    Attributes:
        id (UUID):
        data_product_id (UUID):
    """

    id: UUID
    data_product_id: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        data_product_id = str(self.data_product_id)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "data_product_id": data_product_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        data_product_id = UUID(d.pop("data_product_id"))

        delete_data_product_role_assignment_response = cls(
            id=id,
            data_product_id=data_product_id,
        )

        delete_data_product_role_assignment_response.additional_properties = d
        return delete_data_product_role_assignment_response

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
