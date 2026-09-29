from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.output_port_access_function import OutputPortAccessFunction
from ..types import UNSET, Unset

T = TypeVar("T", bound="OutputPortClassificationCreate")


@_attrs_define
class OutputPortClassificationCreate:
    """
    Attributes:
        name (str):
        access_function (OutputPortAccessFunction):
        description (str | Unset):  Default: ''.
    """

    name: str
    access_function: OutputPortAccessFunction
    description: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        access_function = self.access_function.value

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "access_function": access_function,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        access_function = OutputPortAccessFunction(d.pop("access_function"))

        description = d.pop("description", UNSET)

        output_port_classification_create = cls(
            name=name,
            access_function=access_function,
            description=description,
        )

        output_port_classification_create.additional_properties = d
        return output_port_classification_create

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
