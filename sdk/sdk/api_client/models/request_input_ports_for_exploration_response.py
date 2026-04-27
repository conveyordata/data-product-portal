from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RequestInputPortsForExplorationResponse")


@_attrs_define
class RequestInputPortsForExplorationResponse:
    """
    Attributes:
        input_port_ids (list[UUID]):
    """

    input_port_ids: list[UUID]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        input_port_ids = []
        for input_port_ids_item_data in self.input_port_ids:
            input_port_ids_item = str(input_port_ids_item_data)
            input_port_ids.append(input_port_ids_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "input_port_ids": input_port_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        input_port_ids = []
        _input_port_ids = d.pop("input_port_ids")
        for input_port_ids_item_data in _input_port_ids:
            input_port_ids_item = UUID(input_port_ids_item_data)

            input_port_ids.append(input_port_ids_item)

        request_input_ports_for_exploration_response = cls(
            input_port_ids=input_port_ids,
        )

        request_input_ports_for_exploration_response.additional_properties = d
        return request_input_ports_for_exploration_response

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
