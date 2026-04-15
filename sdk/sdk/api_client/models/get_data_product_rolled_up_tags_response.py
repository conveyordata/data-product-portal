from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.tag import Tag


T = TypeVar("T", bound="GetDataProductRolledUpTagsResponse")


@_attrs_define
class GetDataProductRolledUpTagsResponse:
    """
    Attributes:
        rolled_up_tags (list[Tag]):
    """

    rolled_up_tags: list[Tag]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        rolled_up_tags = []
        for rolled_up_tags_item_data in self.rolled_up_tags:
            rolled_up_tags_item = rolled_up_tags_item_data.to_dict()
            rolled_up_tags.append(rolled_up_tags_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "rolled_up_tags": rolled_up_tags,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tag import Tag

        d = dict(src_dict)
        rolled_up_tags = []
        _rolled_up_tags = d.pop("rolled_up_tags")
        for rolled_up_tags_item_data in _rolled_up_tags:
            rolled_up_tags_item = Tag.from_dict(rolled_up_tags_item_data)

            rolled_up_tags.append(rolled_up_tags_item)

        get_data_product_rolled_up_tags_response = cls(
            rolled_up_tags=rolled_up_tags,
        )

        get_data_product_rolled_up_tags_response.additional_properties = d
        return get_data_product_rolled_up_tags_response

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
