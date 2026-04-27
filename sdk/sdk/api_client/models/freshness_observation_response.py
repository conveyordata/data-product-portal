from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.freshness_status import FreshnessStatus

T = TypeVar("T", bound="FreshnessObservationResponse")


@_attrs_define
class FreshnessObservationResponse:
    """
    Attributes:
        id (UUID):
        output_port_id (UUID):
        last_refreshed_at (datetime.datetime):
        created_at (datetime.datetime):
        status (FreshnessStatus):
    """

    id: UUID
    output_port_id: UUID
    last_refreshed_at: datetime.datetime
    created_at: datetime.datetime
    status: FreshnessStatus
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        output_port_id = str(self.output_port_id)

        last_refreshed_at = self.last_refreshed_at.isoformat()

        created_at = self.created_at.isoformat()

        status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "output_port_id": output_port_id,
                "last_refreshed_at": last_refreshed_at,
                "created_at": created_at,
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        output_port_id = UUID(d.pop("output_port_id"))

        last_refreshed_at = isoparse(d.pop("last_refreshed_at"))

        created_at = isoparse(d.pop("created_at"))

        status = FreshnessStatus(d.pop("status"))

        freshness_observation_response = cls(
            id=id,
            output_port_id=output_port_id,
            last_refreshed_at=last_refreshed_at,
            created_at=created_at,
            status=status,
        )

        freshness_observation_response.additional_properties = d
        return freshness_observation_response

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
