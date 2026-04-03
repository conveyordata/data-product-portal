from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.authorization_action import AuthorizationAction
from ..models.prototype import Prototype
from ..models.scope import Scope

T = TypeVar("T", bound="Role")


@_attrs_define
class Role:
    """
    Attributes:
        name (str):
        scope (Scope):
        description (str):
        permissions (list[AuthorizationAction]):
        id (UUID):
        prototype (Prototype):
    """

    name: str
    scope: Scope
    description: str
    permissions: list[AuthorizationAction]
    id: UUID
    prototype: Prototype
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        scope = self.scope.value

        description = self.description

        permissions = []
        for permissions_item_data in self.permissions:
            permissions_item = permissions_item_data.value
            permissions.append(permissions_item)

        id = str(self.id)

        prototype = self.prototype.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "scope": scope,
                "description": description,
                "permissions": permissions,
                "id": id,
                "prototype": prototype,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        scope = Scope(d.pop("scope"))

        description = d.pop("description")

        permissions = []
        _permissions = d.pop("permissions")
        for permissions_item_data in _permissions:
            permissions_item = AuthorizationAction(permissions_item_data)

            permissions.append(permissions_item)

        id = UUID(d.pop("id"))

        prototype = Prototype(d.pop("prototype"))

        role = cls(
            name=name,
            scope=scope,
            description=description,
            permissions=permissions,
            id=id,
            prototype=prototype,
        )

        role.additional_properties = d
        return role

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
