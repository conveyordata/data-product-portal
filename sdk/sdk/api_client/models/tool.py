from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.tool_base_values import ToolBaseValues


T = TypeVar("T", bound="Tool")


@_attrs_define
class Tool:
    """
    Attributes:
        id (UUID):
        name (str):
        description (str):
        data_product_id (UUID):
        platform_key (str):
        tool_type (str):
        base_values (ToolBaseValues):
    """

    id: UUID
    name: str
    description: str
    data_product_id: UUID
    platform_key: str
    tool_type: str
    base_values: ToolBaseValues
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        description = self.description

        data_product_id = str(self.data_product_id)

        platform_key = self.platform_key

        tool_type = self.tool_type

        base_values = self.base_values.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "data_product_id": data_product_id,
                "platform_key": platform_key,
                "tool_type": tool_type,
                "base_values": base_values,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tool_base_values import ToolBaseValues  # noqa: PLC0415

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        description = d.pop("description")

        data_product_id = UUID(d.pop("data_product_id"))

        platform_key = d.pop("platform_key")

        tool_type = d.pop("tool_type")

        base_values = ToolBaseValues.from_dict(d.pop("base_values"))

        tool = cls(
            id=id,
            name=name,
            description=description,
            data_product_id=data_product_id,
            platform_key=platform_key,
            tool_type=tool_type,
            base_values=base_values,
        )

        tool.additional_properties = d
        return tool

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
