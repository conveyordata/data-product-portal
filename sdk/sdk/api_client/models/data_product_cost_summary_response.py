from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.output_port_cost_breakdown import OutputPortCostBreakdown


T = TypeVar("T", bound="DataProductCostSummaryResponse")


@_attrs_define
class DataProductCostSummaryResponse:
    """
    Attributes:
        data_product_id (UUID):
        day_range (int):
        total_cost (str):
        breakdown (list[OutputPortCostBreakdown]):
    """

    data_product_id: UUID
    day_range: int
    total_cost: str
    breakdown: list[OutputPortCostBreakdown]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data_product_id = str(self.data_product_id)

        day_range = self.day_range

        total_cost = self.total_cost

        breakdown = []
        for breakdown_item_data in self.breakdown:
            breakdown_item = breakdown_item_data.to_dict()
            breakdown.append(breakdown_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_product_id": data_product_id,
                "day_range": day_range,
                "total_cost": total_cost,
                "breakdown": breakdown,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.output_port_cost_breakdown import OutputPortCostBreakdown

        d = dict(src_dict)
        data_product_id = UUID(d.pop("data_product_id"))

        day_range = d.pop("day_range")

        total_cost = d.pop("total_cost")

        breakdown = []
        _breakdown = d.pop("breakdown")
        for breakdown_item_data in _breakdown:
            breakdown_item = OutputPortCostBreakdown.from_dict(breakdown_item_data)

            breakdown.append(breakdown_item)

        data_product_cost_summary_response = cls(
            data_product_id=data_product_id,
            day_range=day_range,
            total_cost=total_cost,
            breakdown=breakdown,
        )

        data_product_cost_summary_response.additional_properties = d
        return data_product_cost_summary_response

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
