from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_abstract_data_product_response import (
        GetAbstractDataProductResponse,
    )
    from ..models.get_output_port_response import GetOutputPortResponse


T = TypeVar("T", bound="OutputPortLinkDeniedEvent")


@_attrs_define
class OutputPortLinkDeniedEvent:
    """
    Attributes:
        abstract_data_product (GetAbstractDataProductResponse):
        output_port (GetOutputPortResponse):
    """

    abstract_data_product: GetAbstractDataProductResponse
    output_port: GetOutputPortResponse
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        abstract_data_product = self.abstract_data_product.to_dict()

        output_port = self.output_port.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "abstract_data_product": abstract_data_product,
                "output_port": output_port,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_abstract_data_product_response import (
            GetAbstractDataProductResponse,
        )
        from ..models.get_output_port_response import GetOutputPortResponse

        d = dict(src_dict)
        abstract_data_product = GetAbstractDataProductResponse.from_dict(
            d.pop("abstract_data_product")
        )

        output_port = GetOutputPortResponse.from_dict(d.pop("output_port"))

        output_port_link_denied_event = cls(
            abstract_data_product=abstract_data_product,
            output_port=output_port,
        )

        output_port_link_denied_event.additional_properties = d
        return output_port_link_denied_event

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
