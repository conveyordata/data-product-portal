from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.decision_status import DecisionStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.output_port import OutputPort


T = TypeVar("T", bound="InputPort")


@_attrs_define
class InputPort:
    """
    Attributes:
        id (UUID):
        justification (str):
        status (DecisionStatus):
        output_port_id (UUID):
        output_port (OutputPort):
        is_expiring_soon (bool):
        expires_on (datetime.datetime | None | Unset):
        requested_duration_days (int | None | Unset):
    """

    id: UUID
    justification: str
    status: DecisionStatus
    output_port_id: UUID
    output_port: OutputPort
    is_expiring_soon: bool
    expires_on: datetime.datetime | None | Unset = UNSET
    requested_duration_days: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        justification = self.justification

        status = self.status.value

        output_port_id = str(self.output_port_id)

        output_port = self.output_port.to_dict()

        is_expiring_soon = self.is_expiring_soon

        expires_on: None | str | Unset
        if isinstance(self.expires_on, Unset):
            expires_on = UNSET
        elif isinstance(self.expires_on, datetime.datetime):
            expires_on = self.expires_on.isoformat()
        else:
            expires_on = self.expires_on

        requested_duration_days: int | None | Unset
        if isinstance(self.requested_duration_days, Unset):
            requested_duration_days = UNSET
        else:
            requested_duration_days = self.requested_duration_days

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "justification": justification,
                "status": status,
                "output_port_id": output_port_id,
                "output_port": output_port,
                "is_expiring_soon": is_expiring_soon,
            }
        )
        if expires_on is not UNSET:
            field_dict["expires_on"] = expires_on
        if requested_duration_days is not UNSET:
            field_dict["requested_duration_days"] = requested_duration_days

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.output_port import OutputPort

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        justification = d.pop("justification")

        status = DecisionStatus(d.pop("status"))

        output_port_id = UUID(d.pop("output_port_id"))

        output_port = OutputPort.from_dict(d.pop("output_port"))

        is_expiring_soon = d.pop("is_expiring_soon")

        def _parse_expires_on(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_on_type_0 = datetime.datetime.fromisoformat(data)

                return expires_on_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        expires_on = _parse_expires_on(d.pop("expires_on", UNSET))

        def _parse_requested_duration_days(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        requested_duration_days = _parse_requested_duration_days(
            d.pop("requested_duration_days", UNSET)
        )

        input_port = cls(
            id=id,
            justification=justification,
            status=status,
            output_port_id=output_port_id,
            output_port=output_port,
            is_expiring_soon=is_expiring_soon,
            expires_on=expires_on,
            requested_duration_days=requested_duration_days,
        )

        input_port.additional_properties = d
        return input_port

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
