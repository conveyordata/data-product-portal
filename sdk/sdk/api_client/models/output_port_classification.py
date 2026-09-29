from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.output_port_access_function import OutputPortAccessFunction

T = TypeVar("T", bound="OutputPortClassification")


@_attrs_define
class OutputPortClassification:
    """
    Attributes:
        id (UUID):
        name (str):
        access_function (OutputPortAccessFunction):
    """

    id: UUID
    name: str
    access_function: OutputPortAccessFunction
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        access_function = self.access_function.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "access_function": access_function,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        access_function = OutputPortAccessFunction(d.pop("access_function"))

        output_port_classification = cls(
            id=id,
            name=name,
            access_function=access_function,
        )

        output_port_classification.additional_properties = d
        return output_port_classification

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
