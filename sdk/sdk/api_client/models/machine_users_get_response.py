from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.machine_user_get import MachineUserGet


T = TypeVar("T", bound="MachineUsersGetResponse")


@_attrs_define
class MachineUsersGetResponse:
    """
    Attributes:
        machine_users (list[MachineUserGet]):
    """

    machine_users: list[MachineUserGet]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        machine_users = []
        for machine_users_item_data in self.machine_users:
            machine_users_item = machine_users_item_data.to_dict()
            machine_users.append(machine_users_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "machine_users": machine_users,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.machine_user_get import MachineUserGet

        d = dict(src_dict)
        machine_users = []
        _machine_users = d.pop("machine_users")
        for machine_users_item_data in _machine_users:
            machine_users_item = MachineUserGet.from_dict(machine_users_item_data)

            machine_users.append(machine_users_item)

        machine_users_get_response = cls(
            machine_users=machine_users,
        )

        machine_users_get_response.additional_properties = d
        return machine_users_get_response

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
