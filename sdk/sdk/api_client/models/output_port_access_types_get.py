from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.output_port_access_types_get_item import OutputPortAccessTypesGetItem


T = TypeVar("T", bound="OutputPortAccessTypesGet")


@_attrs_define
class OutputPortAccessTypesGet:
    """
    Attributes:
        output_port_access_types (list[OutputPortAccessTypesGetItem]):
    """

    output_port_access_types: list[OutputPortAccessTypesGetItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        output_port_access_types = []
        for output_port_access_types_item_data in self.output_port_access_types:
            output_port_access_types_item = output_port_access_types_item_data.to_dict()
            output_port_access_types.append(output_port_access_types_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "output_port_access_types": output_port_access_types,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.output_port_access_types_get_item import (
            OutputPortAccessTypesGetItem,  # noqa: PLC0415
        )

        d = dict(src_dict)
        output_port_access_types = []
        _output_port_access_types = d.pop("output_port_access_types")
        for output_port_access_types_item_data in _output_port_access_types:
            output_port_access_types_item = OutputPortAccessTypesGetItem.from_dict(
                output_port_access_types_item_data
            )

            output_port_access_types.append(output_port_access_types_item)

        output_port_access_types_get = cls(
            output_port_access_types=output_port_access_types,
        )

        output_port_access_types_get.additional_properties = d
        return output_port_access_types_get

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
