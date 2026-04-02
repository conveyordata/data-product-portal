from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DataProductLifeCyclesGetItem")


@_attrs_define
class DataProductLifeCyclesGetItem:
    """
    Attributes:
        id (UUID):
        value (int):
        name (str):
        color (str):
        is_default (bool):
    """

    id: UUID
    value: int
    name: str
    color: str
    is_default: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        value = self.value

        name = self.name

        color = self.color

        is_default = self.is_default

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "value": value,
                "name": name,
                "color": color,
                "is_default": is_default,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        value = d.pop("value")

        name = d.pop("name")

        color = d.pop("color")

        is_default = d.pop("is_default")

        data_product_life_cycles_get_item = cls(
            id=id,
            value=value,
            name=name,
            color=color,
            is_default=is_default,
        )

        data_product_life_cycles_get_item.additional_properties = d
        return data_product_life_cycles_get_item

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
