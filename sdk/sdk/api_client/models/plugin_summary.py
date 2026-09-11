from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.plugin_summary_fields_item import PluginSummaryFieldsItem


T = TypeVar("T", bound="PluginSummary")


@_attrs_define
class PluginSummary:
    """
    Attributes:
        key (str):
        display_name (str):
        fields (list[PluginSummaryFieldsItem]):
    """

    key: str
    display_name: str
    fields: list[PluginSummaryFieldsItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        key = self.key

        display_name = self.display_name

        fields = []
        for fields_item_data in self.fields:
            fields_item = fields_item_data.to_dict()
            fields.append(fields_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
                "display_name": display_name,
                "fields": fields,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.plugin_summary_fields_item import PluginSummaryFieldsItem

        d = dict(src_dict)
        key = d.pop("key")

        display_name = d.pop("display_name")

        fields = []
        _fields = d.pop("fields")
        for fields_item_data in _fields:
            fields_item = PluginSummaryFieldsItem.from_dict(fields_item_data)

            fields.append(fields_item)

        plugin_summary = cls(
            key=key,
            display_name=display_name,
            fields=fields,
        )

        plugin_summary.additional_properties = d
        return plugin_summary

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
