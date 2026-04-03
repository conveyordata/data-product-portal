from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.data_product_life_cycles_get_item import DataProductLifeCyclesGetItem


T = TypeVar("T", bound="DataProductLifeCyclesGet")


@_attrs_define
class DataProductLifeCyclesGet:
    """
    Attributes:
        data_product_life_cycles (list[DataProductLifeCyclesGetItem]):
    """

    data_product_life_cycles: list[DataProductLifeCyclesGetItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data_product_life_cycles = []
        for data_product_life_cycles_item_data in self.data_product_life_cycles:
            data_product_life_cycles_item = data_product_life_cycles_item_data.to_dict()
            data_product_life_cycles.append(data_product_life_cycles_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_product_life_cycles": data_product_life_cycles,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_product_life_cycles_get_item import (
            DataProductLifeCyclesGetItem,
        )

        d = dict(src_dict)
        data_product_life_cycles = []
        _data_product_life_cycles = d.pop("data_product_life_cycles")
        for data_product_life_cycles_item_data in _data_product_life_cycles:
            data_product_life_cycles_item = DataProductLifeCyclesGetItem.from_dict(
                data_product_life_cycles_item_data
            )

            data_product_life_cycles.append(data_product_life_cycles_item)

        data_product_life_cycles_get = cls(
            data_product_life_cycles=data_product_life_cycles,
        )

        data_product_life_cycles_get.additional_properties = d
        return data_product_life_cycles_get

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
