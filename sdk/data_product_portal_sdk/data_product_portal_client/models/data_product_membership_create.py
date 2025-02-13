from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_product_user_role import DataProductUserRole

T = TypeVar("T", bound="DataProductMembershipCreate")


@_attrs_define
class DataProductMembershipCreate:
    """
    Attributes:
        user_id (UUID):
        role (DataProductUserRole):
    """

    user_id: UUID
    role: DataProductUserRole
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = str(self.user_id)

        role = self.role.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "role": role,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        user_id = UUID(d.pop("user_id"))

        role = DataProductUserRole(d.pop("role"))

        data_product_membership_create = cls(
            user_id=user_id,
            role=role,
        )

        data_product_membership_create.additional_properties = d
        return data_product_membership_create

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
