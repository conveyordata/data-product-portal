from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="OutputPortCuratedQuery")


@_attrs_define
class OutputPortCuratedQuery:
    """
    Attributes:
        output_port_id (UUID):
        sort_order (int):
        title (str):
        description (None | str):
        query_text (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime | None):
    """

    output_port_id: UUID
    sort_order: int
    title: str
    description: None | str
    query_text: str
    created_at: datetime.datetime
    updated_at: datetime.datetime | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        output_port_id = str(self.output_port_id)

        sort_order = self.sort_order

        title = self.title

        description: None | str
        description = self.description

        query_text = self.query_text

        created_at = self.created_at.isoformat()

        updated_at: None | str
        if isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "output_port_id": output_port_id,
                "sort_order": sort_order,
                "title": title,
                "description": description,
                "query_text": query_text,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        output_port_id = UUID(d.pop("output_port_id"))

        sort_order = d.pop("sort_order")

        title = d.pop("title")

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        query_text = d.pop("query_text")

        created_at = isoparse(d.pop("created_at"))

        def _parse_updated_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)

                return updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        updated_at = _parse_updated_at(d.pop("updated_at"))

        output_port_curated_query = cls(
            output_port_id=output_port_id,
            sort_order=sort_order,
            title=title,
            description=description,
            query_text=query_text,
            created_at=created_at,
            updated_at=updated_at,
        )

        output_port_curated_query.additional_properties = d
        return output_port_curated_query

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
