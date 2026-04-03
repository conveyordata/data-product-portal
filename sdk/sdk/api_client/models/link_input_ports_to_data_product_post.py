from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="LinkInputPortsToDataProductPost")


@_attrs_define
class LinkInputPortsToDataProductPost:
    """
    Attributes:
        input_port_links (list[UUID]):
    """

    input_port_links: list[UUID]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        input_port_links = []
        for input_port_links_item_data in self.input_port_links:
            input_port_links_item = str(input_port_links_item_data)
            input_port_links.append(input_port_links_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "input_port_links": input_port_links,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        input_port_links = []
        _input_port_links = d.pop("input_port_links")
        for input_port_links_item_data in _input_port_links:
            input_port_links_item = UUID(input_port_links_item_data)

            input_port_links.append(input_port_links_item)

        link_input_ports_to_data_product_post = cls(
            input_port_links=input_port_links,
        )

        link_input_ports_to_data_product_post.additional_properties = d
        return link_input_ports_to_data_product_post

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
