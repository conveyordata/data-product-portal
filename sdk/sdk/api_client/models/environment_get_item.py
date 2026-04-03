from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EnvironmentGetItem")


@_attrs_define
class EnvironmentGetItem:
    """
    Attributes:
        id (UUID):
        name (str):
        acronym (str):
        context (str):
        is_default (bool | Unset):  Default: False.
    """

    id: UUID
    name: str
    acronym: str
    context: str
    is_default: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        acronym = self.acronym

        context = self.context

        is_default = self.is_default

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "acronym": acronym,
                "context": context,
            }
        )
        if is_default is not UNSET:
            field_dict["is_default"] = is_default

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        acronym = d.pop("acronym")

        context = d.pop("context")

        is_default = d.pop("is_default", UNSET)

        environment_get_item = cls(
            id=id,
            name=name,
            acronym=acronym,
            context=context,
            is_default=is_default,
        )

        environment_get_item.additional_properties = d
        return environment_get_item

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
