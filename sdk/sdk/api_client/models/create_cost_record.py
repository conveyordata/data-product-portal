from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateCostRecord")


@_attrs_define
class CreateCostRecord:
    """
    Attributes:
        compute_cost (float | str):
        storage_cost (float | str):
        platform_overhead_cost (float | str):
        recorded_at (datetime.date | None | Unset):
    """

    compute_cost: float | str
    storage_cost: float | str
    platform_overhead_cost: float | str
    recorded_at: datetime.date | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        compute_cost: float | str
        compute_cost = self.compute_cost

        storage_cost: float | str
        storage_cost = self.storage_cost

        platform_overhead_cost: float | str
        platform_overhead_cost = self.platform_overhead_cost

        recorded_at: None | str | Unset
        if isinstance(self.recorded_at, Unset):
            recorded_at = UNSET
        elif isinstance(self.recorded_at, datetime.date):
            recorded_at = self.recorded_at.isoformat()
        else:
            recorded_at = self.recorded_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "compute_cost": compute_cost,
                "storage_cost": storage_cost,
                "platform_overhead_cost": platform_overhead_cost,
            }
        )
        if recorded_at is not UNSET:
            field_dict["recorded_at"] = recorded_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_compute_cost(data: object) -> float | str:
            return cast(float | str, data)

        compute_cost = _parse_compute_cost(d.pop("compute_cost"))

        def _parse_storage_cost(data: object) -> float | str:
            return cast(float | str, data)

        storage_cost = _parse_storage_cost(d.pop("storage_cost"))

        def _parse_platform_overhead_cost(data: object) -> float | str:
            return cast(float | str, data)

        platform_overhead_cost = _parse_platform_overhead_cost(
            d.pop("platform_overhead_cost")
        )

        def _parse_recorded_at(data: object) -> datetime.date | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                recorded_at_type_0 = isoparse(data).date()

                return recorded_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.date | None | Unset, data)

        recorded_at = _parse_recorded_at(d.pop("recorded_at", UNSET))

        create_cost_record = cls(
            compute_cost=compute_cost,
            storage_cost=storage_cost,
            platform_overhead_cost=platform_overhead_cost,
            recorded_at=recorded_at,
        )

        create_cost_record.additional_properties = d
        return create_cost_record

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
