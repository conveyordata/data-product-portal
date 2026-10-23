from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_tool_request_base_values import CreateToolRequestBaseValues


T = TypeVar("T", bound="CreateToolRequest")


@_attrs_define
class CreateToolRequest:
    """
    Attributes:
        name (str):
        platform_key (str):
        tool_type (str):
        description (str | Unset):  Default: ''.
        base_values (CreateToolRequestBaseValues | Unset):
    """

    name: str
    platform_key: str
    tool_type: str
    description: str | Unset = ""
    base_values: CreateToolRequestBaseValues | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        platform_key = self.platform_key

        tool_type = self.tool_type

        description = self.description

        base_values: dict[str, Any] | Unset = UNSET
        if not isinstance(self.base_values, Unset):
            base_values = self.base_values.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "platform_key": platform_key,
                "tool_type": tool_type,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if base_values is not UNSET:
            field_dict["base_values"] = base_values

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_tool_request_base_values import (
            CreateToolRequestBaseValues,  # noqa: PLC0415
        )

        d = dict(src_dict)
        name = d.pop("name")

        platform_key = d.pop("platform_key")

        tool_type = d.pop("tool_type")

        description = d.pop("description", UNSET)

        _base_values = d.pop("base_values", UNSET)
        base_values: CreateToolRequestBaseValues | Unset
        if isinstance(_base_values, Unset):
            base_values = UNSET
        else:
            base_values = CreateToolRequestBaseValues.from_dict(_base_values)

        create_tool_request = cls(
            name=name,
            platform_key=platform_key,
            tool_type=tool_type,
            description=description,
            base_values=base_values,
        )

        create_tool_request.additional_properties = d
        return create_tool_request

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
