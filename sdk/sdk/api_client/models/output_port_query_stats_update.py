from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="OutputPortQueryStatsUpdate")


@_attrs_define
class OutputPortQueryStatsUpdate:
    """
    Attributes:
        date (str):
        consumer_data_product_id (UUID):
        query_count (int):
    """

    date: str
    consumer_data_product_id: UUID
    query_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        date = self.date

        consumer_data_product_id = str(self.consumer_data_product_id)

        query_count = self.query_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "date": date,
                "consumer_data_product_id": consumer_data_product_id,
                "query_count": query_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        date = d.pop("date")

        consumer_data_product_id = UUID(d.pop("consumer_data_product_id"))

        query_count = d.pop("query_count")

        output_port_query_stats_update = cls(
            date=date,
            consumer_data_product_id=consumer_data_product_id,
            query_count=query_count,
        )

        output_port_query_stats_update.additional_properties = d
        return output_port_query_stats_update

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
