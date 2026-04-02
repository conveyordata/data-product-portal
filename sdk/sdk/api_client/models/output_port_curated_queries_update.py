from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.output_port_curated_query_input import OutputPortCuratedQueryInput


T = TypeVar("T", bound="OutputPortCuratedQueriesUpdate")


@_attrs_define
class OutputPortCuratedQueriesUpdate:
    """
    Attributes:
        curated_queries (list[OutputPortCuratedQueryInput]):
    """

    curated_queries: list[OutputPortCuratedQueryInput]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        curated_queries = []
        for curated_queries_item_data in self.curated_queries:
            curated_queries_item = curated_queries_item_data.to_dict()
            curated_queries.append(curated_queries_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "curated_queries": curated_queries,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.output_port_curated_query_input import OutputPortCuratedQueryInput

        d = dict(src_dict)
        curated_queries = []
        _curated_queries = d.pop("curated_queries")
        for curated_queries_item_data in _curated_queries:
            curated_queries_item = OutputPortCuratedQueryInput.from_dict(
                curated_queries_item_data
            )

            curated_queries.append(curated_queries_item)

        output_port_curated_queries_update = cls(
            curated_queries=curated_queries,
        )

        output_port_curated_queries_update.additional_properties = d
        return output_port_curated_queries_update

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
