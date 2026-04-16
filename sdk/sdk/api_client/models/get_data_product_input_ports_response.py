from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.input_port import InputPort


T = TypeVar("T", bound="GetDataProductInputPortsResponse")


@_attrs_define
class GetDataProductInputPortsResponse:
    """
    Attributes:
        input_ports (list[InputPort]):
    """

    input_ports: list[InputPort]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        input_ports = []
        for input_ports_item_data in self.input_ports:
            input_ports_item = input_ports_item_data.to_dict()
            input_ports.append(input_ports_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "input_ports": input_ports,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.input_port import InputPort

        d = dict(src_dict)
        input_ports = []
        _input_ports = d.pop("input_ports")
        for input_ports_item_data in _input_ports:
            input_ports_item = InputPort.from_dict(input_ports_item_data)

            input_ports.append(input_ports_item)

        get_data_product_input_ports_response = cls(
            input_ports=input_ports,
        )

        get_data_product_input_ports_response.additional_properties = d
        return get_data_product_input_ports_response

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
