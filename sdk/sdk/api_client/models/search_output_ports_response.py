from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.search_output_ports_response_item import SearchOutputPortsResponseItem


T = TypeVar("T", bound="SearchOutputPortsResponse")


@_attrs_define
class SearchOutputPortsResponse:
    """
    Attributes:
        output_ports (list[SearchOutputPortsResponseItem]):
    """

    output_ports: list[SearchOutputPortsResponseItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        output_ports = []
        for output_ports_item_data in self.output_ports:
            output_ports_item = output_ports_item_data.to_dict()
            output_ports.append(output_ports_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "output_ports": output_ports,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.search_output_ports_response_item import (
            SearchOutputPortsResponseItem,
        )

        d = dict(src_dict)
        output_ports = []
        _output_ports = d.pop("output_ports")
        for output_ports_item_data in _output_ports:
            output_ports_item = SearchOutputPortsResponseItem.from_dict(
                output_ports_item_data
            )

            output_ports.append(output_ports_item)

        search_output_ports_response = cls(
            output_ports=output_ports,
        )

        search_output_ports_response.additional_properties = d
        return search_output_ports_response

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
