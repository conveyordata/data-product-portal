from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_product_icon_key import DataProductIconKey

T = TypeVar("T", bound="DataProductTypesGetItem")


@_attrs_define
class DataProductTypesGetItem:
    """
    Attributes:
        id (UUID):
        name (str):
        description (str):
        icon_key (DataProductIconKey):
        data_product_count (int):
    """

    id: UUID
    name: str
    description: str
    icon_key: DataProductIconKey
    data_product_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        description = self.description

        icon_key = self.icon_key.value

        data_product_count = self.data_product_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "icon_key": icon_key,
                "data_product_count": data_product_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        description = d.pop("description")

        icon_key = DataProductIconKey(d.pop("icon_key"))

        data_product_count = d.pop("data_product_count")

        data_product_types_get_item = cls(
            id=id,
            name=name,
            description=description,
            icon_key=icon_key,
            data_product_count=data_product_count,
        )

        data_product_types_get_item.additional_properties = d
        return data_product_types_get_item

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
