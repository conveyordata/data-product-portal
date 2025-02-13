from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DataOutputUpdate")


@_attrs_define
class DataOutputUpdate:
    """
    Attributes:
        name (str):
        description (str):
        tag_ids (list[UUID]):
    """

    name: str
    description: str
    tag_ids: list[UUID]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        tag_ids = []
        for tag_ids_item_data in self.tag_ids:
            tag_ids_item = str(tag_ids_item_data)
            tag_ids.append(tag_ids_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "tag_ids": tag_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        tag_ids = []
        _tag_ids = d.pop("tag_ids")
        for tag_ids_item_data in _tag_ids:
            tag_ids_item = UUID(tag_ids_item_data)

            tag_ids.append(tag_ids_item)

        data_output_update = cls(
            name=name,
            description=description,
            tag_ids=tag_ids,
        )

        data_output_update.additional_properties = d
        return data_output_update

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
