from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DenyOutputPortAsInputPortRequest")


@_attrs_define
class DenyOutputPortAsInputPortRequest:
    """
    Attributes:
        consuming_data_product_id (UUID):
    """

    consuming_data_product_id: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        consuming_data_product_id = str(self.consuming_data_product_id)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "consuming_data_product_id": consuming_data_product_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        consuming_data_product_id = UUID(d.pop("consuming_data_product_id"))

        deny_output_port_as_input_port_request = cls(
            consuming_data_product_id=consuming_data_product_id,
        )

        deny_output_port_as_input_port_request.additional_properties = d
        return deny_output_port_as_input_port_request

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
