from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RequestInputPortsForExplorationRequest")


@_attrs_define
class RequestInputPortsForExplorationRequest:
    """
    Attributes:
        output_ports (list[UUID]):
        justification (str):
    """

    output_ports: list[UUID]
    justification: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        output_ports = []
        for output_ports_item_data in self.output_ports:
            output_ports_item = str(output_ports_item_data)
            output_ports.append(output_ports_item)

        justification = self.justification

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "output_ports": output_ports,
                "justification": justification,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        output_ports = []
        _output_ports = d.pop("output_ports")
        for output_ports_item_data in _output_ports:
            output_ports_item = UUID(output_ports_item_data)

            output_ports.append(output_ports_item)

        justification = d.pop("justification")

        request_input_ports_for_exploration_request = cls(
            output_ports=output_ports,
            justification=justification,
        )

        request_input_ports_for_exploration_request.additional_properties = d
        return request_input_ports_for_exploration_request

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
