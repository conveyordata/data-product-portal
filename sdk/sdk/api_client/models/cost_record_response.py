from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="CostRecordResponse")


@_attrs_define
class CostRecordResponse:
    """
    Attributes:
        id (UUID):
        output_port_id (UUID):
        recorded_at (datetime.date):
        compute_cost (str):
        storage_cost (str):
        platform_overhead_cost (str):
        total_cost (str):
    """

    id: UUID
    output_port_id: UUID
    recorded_at: datetime.date
    compute_cost: str
    storage_cost: str
    platform_overhead_cost: str
    total_cost: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        output_port_id = str(self.output_port_id)

        recorded_at = self.recorded_at.isoformat()

        compute_cost = self.compute_cost

        storage_cost = self.storage_cost

        platform_overhead_cost = self.platform_overhead_cost

        total_cost = self.total_cost

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "output_port_id": output_port_id,
                "recorded_at": recorded_at,
                "compute_cost": compute_cost,
                "storage_cost": storage_cost,
                "platform_overhead_cost": platform_overhead_cost,
                "total_cost": total_cost,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        output_port_id = UUID(d.pop("output_port_id"))

        recorded_at = isoparse(d.pop("recorded_at")).date()

        compute_cost = d.pop("compute_cost")

        storage_cost = d.pop("storage_cost")

        platform_overhead_cost = d.pop("platform_overhead_cost")

        total_cost = d.pop("total_cost")

        cost_record_response = cls(
            id=id,
            output_port_id=output_port_id,
            recorded_at=recorded_at,
            compute_cost=compute_cost,
            storage_cost=storage_cost,
            platform_overhead_cost=platform_overhead_cost,
            total_cost=total_cost,
        )

        cost_record_response.additional_properties = d
        return cost_record_response

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
