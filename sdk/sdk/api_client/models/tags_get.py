from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.tags_get_item import TagsGetItem


T = TypeVar("T", bound="TagsGet")


@_attrs_define
class TagsGet:
    """
    Attributes:
        tags (list[TagsGetItem]):
    """

    tags: list[TagsGetItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tags": tags,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tags_get_item import TagsGetItem

        d = dict(src_dict)
        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = TagsGetItem.from_dict(tags_item_data)

            tags.append(tags_item)

        tags_get = cls(
            tags=tags,
        )

        tags_get.additional_properties = d
        return tags_get

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
