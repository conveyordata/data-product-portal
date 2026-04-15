from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="LinkInputPortsToDataProduct")


@_attrs_define
class LinkInputPortsToDataProduct:
    """
    Attributes:
        input_ports (list[UUID]):
        justification (str):
    """

    input_ports: list[UUID]
    justification: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        input_ports = []
        for input_ports_item_data in self.input_ports:
            input_ports_item = str(input_ports_item_data)
            input_ports.append(input_ports_item)

        justification = self.justification

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "input_ports": input_ports,
                "justification": justification,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        input_ports = []
        _input_ports = d.pop("input_ports")
        for input_ports_item_data in _input_ports:
            input_ports_item = UUID(input_ports_item_data)

            input_ports.append(input_ports_item)

        justification = d.pop("justification")

        link_input_ports_to_data_product = cls(
            input_ports=input_ports,
            justification=justification,
        )

        link_input_ports_to_data_product.additional_properties = d
        return link_input_ports_to_data_product

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
