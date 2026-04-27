from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.freshness_status import FreshnessStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="FreshnessSloResponse")


@_attrs_define
class FreshnessSloResponse:
    """
    Attributes:
        id (UUID):
        output_port_id (UUID):
        deadline_time (str):
        status (FreshnessStatus):
        last_refreshed_at (datetime.datetime | None | Unset):
        last_observed_at (datetime.datetime | None | Unset):
    """

    id: UUID
    output_port_id: UUID
    deadline_time: str
    status: FreshnessStatus
    last_refreshed_at: datetime.datetime | None | Unset = UNSET
    last_observed_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        output_port_id = str(self.output_port_id)

        deadline_time = self.deadline_time

        status = self.status.value

        last_refreshed_at: None | str | Unset
        if isinstance(self.last_refreshed_at, Unset):
            last_refreshed_at = UNSET
        elif isinstance(self.last_refreshed_at, datetime.datetime):
            last_refreshed_at = self.last_refreshed_at.isoformat()
        else:
            last_refreshed_at = self.last_refreshed_at

        last_observed_at: None | str | Unset
        if isinstance(self.last_observed_at, Unset):
            last_observed_at = UNSET
        elif isinstance(self.last_observed_at, datetime.datetime):
            last_observed_at = self.last_observed_at.isoformat()
        else:
            last_observed_at = self.last_observed_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "output_port_id": output_port_id,
                "deadline_time": deadline_time,
                "status": status,
            }
        )
        if last_refreshed_at is not UNSET:
            field_dict["last_refreshed_at"] = last_refreshed_at
        if last_observed_at is not UNSET:
            field_dict["last_observed_at"] = last_observed_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        output_port_id = UUID(d.pop("output_port_id"))

        deadline_time = d.pop("deadline_time")

        status = FreshnessStatus(d.pop("status"))

        def _parse_last_refreshed_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_refreshed_at_type_0 = isoparse(data)

                return last_refreshed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        last_refreshed_at = _parse_last_refreshed_at(d.pop("last_refreshed_at", UNSET))

        def _parse_last_observed_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_observed_at_type_0 = isoparse(data)

                return last_observed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        last_observed_at = _parse_last_observed_at(d.pop("last_observed_at", UNSET))

        freshness_slo_response = cls(
            id=id,
            output_port_id=output_port_id,
            deadline_time=deadline_time,
            status=status,
            last_refreshed_at=last_refreshed_at,
            last_observed_at=last_observed_at,
        )

        freshness_slo_response.additional_properties = d
        return freshness_slo_response

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
