from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="MachineUserUpdate")


@_attrs_define
class MachineUserUpdate:
    """
    Attributes:
        display_name (str):
    """

    display_name: str

    def to_dict(self) -> dict[str, Any]:
        display_name = self.display_name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "display_name": display_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        display_name = d.pop("display_name")

        machine_user_update = cls(
            display_name=display_name,
        )

        return machine_user_update
