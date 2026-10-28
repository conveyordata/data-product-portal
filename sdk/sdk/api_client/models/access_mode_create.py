from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AccessModeCreate")


@_attrs_define
class AccessModeCreate:
    """
    Attributes:
        name (str):
        description (str):
        technical_asset_types (list[str]):
    """

    name: str
    description: str
    technical_asset_types: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        technical_asset_types = self.technical_asset_types

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "technical_asset_types": technical_asset_types,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        technical_asset_types = cast(list[str], d.pop("technical_asset_types"))

        access_mode_create = cls(
            name=name,
            description=description,
            technical_asset_types=technical_asset_types,
        )

        access_mode_create.additional_properties = d
        return access_mode_create

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
