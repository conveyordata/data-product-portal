from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    cast,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreateGlobalRoleAssignment")


@_attrs_define
class CreateGlobalRoleAssignment:
    """
    Attributes:
        user_id (UUID):
        role_id (Literal['admin'] | UUID):
    """

    user_id: UUID
    role_id: Literal["admin"] | UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = str(self.user_id)

        role_id: Literal["admin"] | str
        if isinstance(self.role_id, UUID):
            role_id = str(self.role_id)
        else:
            role_id = self.role_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "role_id": role_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = UUID(d.pop("user_id"))

        def _parse_role_id(data: object) -> Literal["admin"] | UUID:
            try:
                if not isinstance(data, str):
                    raise TypeError()
                role_id_type_0 = UUID(data)

                return role_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            role_id_type_1 = cast(Literal["admin"], data)
            if role_id_type_1 != "admin":
                raise ValueError(
                    f"role_id_type_1 must match const 'admin', got '{role_id_type_1}'"
                )
            return role_id_type_1

        role_id = _parse_role_id(d.pop("role_id"))

        create_global_role_assignment = cls(
            user_id=user_id,
            role_id=role_id,
        )

        create_global_role_assignment.additional_properties = d
        return create_global_role_assignment

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
