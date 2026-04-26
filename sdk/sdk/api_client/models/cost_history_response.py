from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.cost_record_response import CostRecordResponse


T = TypeVar("T", bound="CostHistoryResponse")


@_attrs_define
class CostHistoryResponse:
    """
    Attributes:
        output_port_id (UUID):
        records (list[CostRecordResponse]):
    """

    output_port_id: UUID
    records: list[CostRecordResponse]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        output_port_id = str(self.output_port_id)

        records = []
        for records_item_data in self.records:
            records_item = records_item_data.to_dict()
            records.append(records_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "output_port_id": output_port_id,
                "records": records,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cost_record_response import CostRecordResponse

        d = dict(src_dict)
        output_port_id = UUID(d.pop("output_port_id"))

        records = []
        _records = d.pop("records")
        for records_item_data in _records:
            records_item = CostRecordResponse.from_dict(records_item_data)

            records.append(records_item)

        cost_history_response = cls(
            output_port_id=output_port_id,
            records=records,
        )

        cost_history_response.additional_properties = d
        return cost_history_response

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
