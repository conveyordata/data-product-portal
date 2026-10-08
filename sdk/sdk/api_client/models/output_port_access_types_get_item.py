from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.output_port_access_function import OutputPortAccessFunction
from ..types import UNSET, Unset

T = TypeVar("T", bound="OutputPortAccessTypesGetItem")


@_attrs_define
class OutputPortAccessTypesGetItem:
    """
    Attributes:
        id (UUID):
        name (str):
        access_function (OutputPortAccessFunction):
        description (str):
        output_port_count (int | None | Unset):
    """

    id: UUID
    name: str
    access_function: OutputPortAccessFunction
    description: str
    output_port_count: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        access_function = self.access_function.value

        description = self.description

        output_port_count: int | None | Unset
        if isinstance(self.output_port_count, Unset):
            output_port_count = UNSET
        else:
            output_port_count = self.output_port_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "access_function": access_function,
                "description": description,
            }
        )
        if output_port_count is not UNSET:
            field_dict["output_port_count"] = output_port_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        access_function = OutputPortAccessFunction(d.pop("access_function"))

        description = d.pop("description")

        def _parse_output_port_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        output_port_count = _parse_output_port_count(d.pop("output_port_count", UNSET))

        output_port_access_types_get_item = cls(
            id=id,
            name=name,
            access_function=access_function,
            description=description,
            output_port_count=output_port_count,
        )

        output_port_access_types_get_item.additional_properties = d
        return output_port_access_types_get_item

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
