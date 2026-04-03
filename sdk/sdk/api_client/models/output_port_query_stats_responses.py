from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.output_port_query_stats_response import OutputPortQueryStatsResponse


T = TypeVar("T", bound="OutputPortQueryStatsResponses")


@_attrs_define
class OutputPortQueryStatsResponses:
    """
    Attributes:
        output_port_query_stats_responses (list[OutputPortQueryStatsResponse]):
    """

    output_port_query_stats_responses: list[OutputPortQueryStatsResponse]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        output_port_query_stats_responses = []
        for (
            output_port_query_stats_responses_item_data
        ) in self.output_port_query_stats_responses:
            output_port_query_stats_responses_item = (
                output_port_query_stats_responses_item_data.to_dict()
            )
            output_port_query_stats_responses.append(
                output_port_query_stats_responses_item
            )

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "output_port_query_stats_responses": output_port_query_stats_responses,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.output_port_query_stats_response import (
            OutputPortQueryStatsResponse,
        )

        d = dict(src_dict)
        output_port_query_stats_responses = []
        _output_port_query_stats_responses = d.pop("output_port_query_stats_responses")
        for (
            output_port_query_stats_responses_item_data
        ) in _output_port_query_stats_responses:
            output_port_query_stats_responses_item = (
                OutputPortQueryStatsResponse.from_dict(
                    output_port_query_stats_responses_item_data
                )
            )

            output_port_query_stats_responses.append(
                output_port_query_stats_responses_item
            )

        output_port_query_stats_responses = cls(
            output_port_query_stats_responses=output_port_query_stats_responses,
        )

        output_port_query_stats_responses.additional_properties = d
        return output_port_query_stats_responses

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
