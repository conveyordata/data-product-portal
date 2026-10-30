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

T = TypeVar("T", bound="GroupIdentity")


@_attrs_define
class GroupIdentity:
    """
    Attributes:
        id (UUID):
        external_id (str):
        display_name (str):
        type_ (Literal['group']):
    """

    id: UUID
    external_id: str
    display_name: str
    type_: Literal["group"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        external_id = self.external_id

        display_name = self.display_name

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "external_id": external_id,
                "display_name": display_name,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        external_id = d.pop("external_id")

        display_name = d.pop("display_name")

        type_ = cast(Literal["group"], d.pop("type"))
        if type_ != "group":
            raise ValueError(f"type must match const 'group', got '{type_}'")

        group_identity = cls(
            id=id,
            external_id=external_id,
            display_name=display_name,
            type_=type_,
        )

        group_identity.additional_properties = d
        return group_identity

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
