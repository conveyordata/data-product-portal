from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_product_membership_status import DataProductMembershipStatus
from ..models.data_product_user_role import DataProductUserRole

if TYPE_CHECKING:
    from ..models.data_product import DataProduct
    from ..models.user import User


T = TypeVar("T", bound="DataProductMembershipGet")


@_attrs_define
class DataProductMembershipGet:
    """
    Attributes:
        id (UUID):
        user_id (UUID):
        data_product_id (UUID):
        role (DataProductUserRole):
        status (DataProductMembershipStatus):
        user (User):
        data_product (DataProduct):
    """

    id: UUID
    user_id: UUID
    data_product_id: UUID
    role: DataProductUserRole
    status: DataProductMembershipStatus
    user: "User"
    data_product: "DataProduct"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        user_id = str(self.user_id)

        data_product_id = str(self.data_product_id)

        role = self.role.value

        status = self.status.value

        user = self.user.to_dict()

        data_product = self.data_product.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "user_id": user_id,
                "data_product_id": data_product_id,
                "role": role,
                "status": status,
                "user": user,
                "data_product": data_product,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.data_product import DataProduct
        from ..models.user import User

        d = src_dict.copy()
        id = UUID(d.pop("id"))

        user_id = UUID(d.pop("user_id"))

        data_product_id = UUID(d.pop("data_product_id"))

        role = DataProductUserRole(d.pop("role"))

        status = DataProductMembershipStatus(d.pop("status"))

        user = User.from_dict(d.pop("user"))

        data_product = DataProduct.from_dict(d.pop("data_product"))

        data_product_membership_get = cls(
            id=id,
            user_id=user_id,
            data_product_id=data_product_id,
            role=role,
            status=status,
            user=user,
            data_product=data_product,
        )

        data_product_membership_get.additional_properties = d
        return data_product_membership_get

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
