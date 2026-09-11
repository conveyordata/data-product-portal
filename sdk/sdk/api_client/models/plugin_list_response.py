from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.plugin_summary import PluginSummary


T = TypeVar("T", bound="PluginListResponse")


@_attrs_define
class PluginListResponse:
    """
    Attributes:
        plugins (list[PluginSummary]):
    """

    plugins: list[PluginSummary]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        plugins = []
        for plugins_item_data in self.plugins:
            plugins_item = plugins_item_data.to_dict()
            plugins.append(plugins_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "plugins": plugins,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.plugin_summary import PluginSummary

        d = dict(src_dict)
        plugins = []
        _plugins = d.pop("plugins")
        for plugins_item_data in _plugins:
            plugins_item = PluginSummary.from_dict(plugins_item_data)

            plugins.append(plugins_item)

        plugin_list_response = cls(
            plugins=plugins,
        )

        plugin_list_response.additional_properties = d
        return plugin_list_response

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
