from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.authorization_action import AuthorizationAction
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateRole")


@_attrs_define
class UpdateRole:
    """
    Attributes:
        name (None | str | Unset):
        description (None | str | Unset):
        permissions (list[AuthorizationAction] | None | Unset):
    """

    name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    permissions: list[AuthorizationAction] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        permissions: list[int] | None | Unset
        if isinstance(self.permissions, Unset):
            permissions = UNSET
        elif isinstance(self.permissions, list):
            permissions = []
            for permissions_type_0_item_data in self.permissions:
                permissions_type_0_item = permissions_type_0_item_data.value
                permissions.append(permissions_type_0_item)

        else:
            permissions = self.permissions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if permissions is not UNSET:
            field_dict["permissions"] = permissions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_permissions(
            data: object,
        ) -> list[AuthorizationAction] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                permissions_type_0 = []
                _permissions_type_0 = data
                for permissions_type_0_item_data in _permissions_type_0:
                    permissions_type_0_item = AuthorizationAction(
                        permissions_type_0_item_data
                    )

                    permissions_type_0.append(permissions_type_0_item)

                return permissions_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[AuthorizationAction] | None | Unset, data)

        permissions = _parse_permissions(d.pop("permissions", UNSET))

        update_role = cls(
            name=name,
            description=description,
            permissions=permissions,
        )

        update_role.additional_properties = d
        return update_role

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
