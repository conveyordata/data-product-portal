from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PlatformTile")


@_attrs_define
class PlatformTile:
    """Represents a platform tile in the UI

    Attributes:
        label (str):
        value (str):
        icon_name (str):
        has_environments (bool | Unset):  Default: True.
        has_config (bool | Unset):  Default: True.
        children (list[PlatformTile] | Unset):
        show_in_form (bool | Unset):  Default: True.
    """

    label: str
    value: str
    icon_name: str
    has_environments: bool | Unset = True
    has_config: bool | Unset = True
    children: list[PlatformTile] | Unset = UNSET
    show_in_form: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        value = self.value

        icon_name = self.icon_name

        has_environments = self.has_environments

        has_config = self.has_config

        children: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.children, Unset):
            children = []
            for children_item_data in self.children:
                children_item = children_item_data.to_dict()
                children.append(children_item)

        show_in_form = self.show_in_form

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "label": label,
                "value": value,
                "icon_name": icon_name,
            }
        )
        if has_environments is not UNSET:
            field_dict["has_environments"] = has_environments
        if has_config is not UNSET:
            field_dict["has_config"] = has_config
        if children is not UNSET:
            field_dict["children"] = children
        if show_in_form is not UNSET:
            field_dict["show_in_form"] = show_in_form

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        label = d.pop("label")

        value = d.pop("value")

        icon_name = d.pop("icon_name")

        has_environments = d.pop("has_environments", UNSET)

        has_config = d.pop("has_config", UNSET)

        _children = d.pop("children", UNSET)
        children: list[PlatformTile] | Unset = UNSET
        if _children is not UNSET:
            children = []
            for children_item_data in _children:
                children_item = PlatformTile.from_dict(children_item_data)

                children.append(children_item)

        show_in_form = d.pop("show_in_form", UNSET)

        platform_tile = cls(
            label=label,
            value=value,
            icon_name=icon_name,
            has_environments=has_environments,
            has_config=has_config,
            children=children,
            show_in_form=show_in_form,
        )

        platform_tile.additional_properties = d
        return platform_tile

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
