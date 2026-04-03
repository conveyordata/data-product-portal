from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="OutputPortQueryStatsResponse")


@_attrs_define
class OutputPortQueryStatsResponse:
    """
    Attributes:
        date (datetime.date):
        consumer_data_product_id (UUID):
        query_count (int):
        consumer_data_product_name (None | str | Unset):
    """

    date: datetime.date
    consumer_data_product_id: UUID
    query_count: int
    consumer_data_product_name: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        date = self.date.isoformat()

        consumer_data_product_id = str(self.consumer_data_product_id)

        query_count = self.query_count

        consumer_data_product_name: None | str | Unset
        if isinstance(self.consumer_data_product_name, Unset):
            consumer_data_product_name = UNSET
        else:
            consumer_data_product_name = self.consumer_data_product_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "date": date,
                "consumer_data_product_id": consumer_data_product_id,
                "query_count": query_count,
            }
        )
        if consumer_data_product_name is not UNSET:
            field_dict["consumer_data_product_name"] = consumer_data_product_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        date = isoparse(d.pop("date")).date()

        consumer_data_product_id = UUID(d.pop("consumer_data_product_id"))

        query_count = d.pop("query_count")

        def _parse_consumer_data_product_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        consumer_data_product_name = _parse_consumer_data_product_name(
            d.pop("consumer_data_product_name", UNSET)
        )

        output_port_query_stats_response = cls(
            date=date,
            consumer_data_product_id=consumer_data_product_id,
            query_count=query_count,
            consumer_data_product_name=consumer_data_product_name,
        )

        output_port_query_stats_response.additional_properties = d
        return output_port_query_stats_response

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
