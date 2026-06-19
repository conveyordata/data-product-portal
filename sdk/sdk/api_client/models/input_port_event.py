from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.abstract_data_product_type import AbstractDataProductType

T = TypeVar("T", bound="InputPortEvent")


@_attrs_define
class InputPortEvent:
    """
    Attributes:
        id (UUID):
        consuming_abstract_data_product_id (UUID):
        consuming_abstract_data_product_type (AbstractDataProductType):
    """

    id: UUID
    consuming_abstract_data_product_id: UUID
    consuming_abstract_data_product_type: AbstractDataProductType
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        consuming_abstract_data_product_id = str(
            self.consuming_abstract_data_product_id
        )

        consuming_abstract_data_product_type = (
            self.consuming_abstract_data_product_type.value
        )

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "consuming_abstract_data_product_id": consuming_abstract_data_product_id,
                "consuming_abstract_data_product_type": consuming_abstract_data_product_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        consuming_abstract_data_product_id = UUID(
            d.pop("consuming_abstract_data_product_id")
        )

        consuming_abstract_data_product_type = AbstractDataProductType(
            d.pop("consuming_abstract_data_product_type")
        )

        input_port_event = cls(
            id=id,
            consuming_abstract_data_product_id=consuming_abstract_data_product_id,
            consuming_abstract_data_product_type=consuming_abstract_data_product_type,
        )

        input_port_event.additional_properties = d
        return input_port_event

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
