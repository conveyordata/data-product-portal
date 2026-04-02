from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_product_icon_key import DataProductIconKey

if TYPE_CHECKING:
    from ..models.data_product import DataProduct


T = TypeVar("T", bound="DataProductTypeGet")


@_attrs_define
class DataProductTypeGet:
    """
    Attributes:
        id (UUID):
        name (str):
        description (str):
        icon_key (DataProductIconKey):
        data_products (list[DataProduct]):
    """

    id: UUID
    name: str
    description: str
    icon_key: DataProductIconKey
    data_products: list[DataProduct]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        description = self.description

        icon_key = self.icon_key.value

        data_products = []
        for data_products_item_data in self.data_products:
            data_products_item = data_products_item_data.to_dict()
            data_products.append(data_products_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "icon_key": icon_key,
                "data_products": data_products,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_product import DataProduct

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        description = d.pop("description")

        icon_key = DataProductIconKey(d.pop("icon_key"))

        data_products = []
        _data_products = d.pop("data_products")
        for data_products_item_data in _data_products:
            data_products_item = DataProduct.from_dict(data_products_item_data)

            data_products.append(data_products_item)

        data_product_type_get = cls(
            id=id,
            name=name,
            description=description,
            icon_key=icon_key,
            data_products=data_products,
        )

        data_product_type_get.additional_properties = d
        return data_product_type_get

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
