from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.data_product_types_get_item import DataProductTypesGetItem


T = TypeVar("T", bound="DataProductTypesGet")


@_attrs_define
class DataProductTypesGet:
    """
    Attributes:
        data_product_types (list[DataProductTypesGetItem]):
    """

    data_product_types: list[DataProductTypesGetItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data_product_types = []
        for data_product_types_item_data in self.data_product_types:
            data_product_types_item = data_product_types_item_data.to_dict()
            data_product_types.append(data_product_types_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_product_types": data_product_types,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_product_types_get_item import DataProductTypesGetItem

        d = dict(src_dict)
        data_product_types = []
        _data_product_types = d.pop("data_product_types")
        for data_product_types_item_data in _data_product_types:
            data_product_types_item = DataProductTypesGetItem.from_dict(
                data_product_types_item_data
            )

            data_product_types.append(data_product_types_item)

        data_product_types_get = cls(
            data_product_types=data_product_types,
        )

        data_product_types_get.additional_properties = d
        return data_product_types_get

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
