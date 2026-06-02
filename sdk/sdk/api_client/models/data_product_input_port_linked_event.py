from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_data_product_response import GetDataProductResponse


T = TypeVar("T", bound="DataProductInputPortLinkedEvent")


@_attrs_define
class DataProductInputPortLinkedEvent:
    """
    Attributes:
        data_product (GetDataProductResponse):
    """

    data_product: GetDataProductResponse
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data_product = self.data_product.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_product": data_product,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_data_product_response import GetDataProductResponse

        d = dict(src_dict)
        data_product = GetDataProductResponse.from_dict(d.pop("data_product"))

        data_product_input_port_linked_event = cls(
            data_product=data_product,
        )

        data_product_input_port_linked_event.additional_properties = d
        return data_product_input_port_linked_event

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
