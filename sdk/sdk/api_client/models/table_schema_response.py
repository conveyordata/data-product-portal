from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.column_response import ColumnResponse
    from ..models.tag import Tag


T = TypeVar("T", bound="TableSchemaResponse")


@_attrs_define
class TableSchemaResponse:
    """
    Attributes:
        id (UUID):
        output_port_id (UUID):
        name (str):
        tags (list[Tag]):
        columns (list[ColumnResponse]):
        description (None | str | Unset):
    """

    id: UUID
    output_port_id: UUID
    name: str
    tags: list[Tag]
    columns: list[ColumnResponse]
    description: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        output_port_id = str(self.output_port_id)

        name = self.name

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        columns = []
        for columns_item_data in self.columns:
            columns_item = columns_item_data.to_dict()
            columns.append(columns_item)

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "output_port_id": output_port_id,
                "name": name,
                "tags": tags,
                "columns": columns,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.column_response import ColumnResponse
        from ..models.tag import Tag

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        output_port_id = UUID(d.pop("output_port_id"))

        name = d.pop("name")

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        columns = []
        _columns = d.pop("columns")
        for columns_item_data in _columns:
            columns_item = ColumnResponse.from_dict(columns_item_data)

            columns.append(columns_item)

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        table_schema_response = cls(
            id=id,
            output_port_id=output_port_id,
            name=name,
            tags=tags,
            columns=columns,
            description=description,
        )

        table_schema_response.additional_properties = d
        return table_schema_response

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
