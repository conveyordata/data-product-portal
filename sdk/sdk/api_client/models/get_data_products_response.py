from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_data_products_response_item import GetDataProductsResponseItem


T = TypeVar("T", bound="GetDataProductsResponse")


@_attrs_define
class GetDataProductsResponse:
    """
    Attributes:
        data_products (list[GetDataProductsResponseItem]):
    """

    data_products: list[GetDataProductsResponseItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data_products = []
        for data_products_item_data in self.data_products:
            data_products_item = data_products_item_data.to_dict()
            data_products.append(data_products_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_products": data_products,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_data_products_response_item import GetDataProductsResponseItem

        d = dict(src_dict)
        data_products = []
        _data_products = d.pop("data_products")
        for data_products_item_data in _data_products:
            data_products_item = GetDataProductsResponseItem.from_dict(
                data_products_item_data
            )

            data_products.append(data_products_item)

        get_data_products_response = cls(
            data_products=data_products,
        )

        get_data_products_response.additional_properties = d
        return get_data_products_response

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
