from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.output_port_query_stats_update import OutputPortQueryStatsUpdate


T = TypeVar("T", bound="UpdateOutputPortQueryStatus")


@_attrs_define
class UpdateOutputPortQueryStatus:
    """
    Attributes:
        output_port_query_stats_updates (list[OutputPortQueryStatsUpdate]):
    """

    output_port_query_stats_updates: list[OutputPortQueryStatsUpdate]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        output_port_query_stats_updates = []
        for (
            output_port_query_stats_updates_item_data
        ) in self.output_port_query_stats_updates:
            output_port_query_stats_updates_item = (
                output_port_query_stats_updates_item_data.to_dict()
            )
            output_port_query_stats_updates.append(output_port_query_stats_updates_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "output_port_query_stats_updates": output_port_query_stats_updates,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.output_port_query_stats_update import OutputPortQueryStatsUpdate

        d = dict(src_dict)
        output_port_query_stats_updates = []
        _output_port_query_stats_updates = d.pop("output_port_query_stats_updates")
        for (
            output_port_query_stats_updates_item_data
        ) in _output_port_query_stats_updates:
            output_port_query_stats_updates_item = OutputPortQueryStatsUpdate.from_dict(
                output_port_query_stats_updates_item_data
            )

            output_port_query_stats_updates.append(output_port_query_stats_updates_item)

        update_output_port_query_status = cls(
            output_port_query_stats_updates=output_port_query_stats_updates,
        )

        update_output_port_query_status.additional_properties = d
        return update_output_port_query_status

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
