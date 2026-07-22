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
    from ..models.user import User


T = TypeVar("T", bound="InputPortRequestBase")


@_attrs_define
class InputPortRequestBase:
    """
    Attributes:
        id (UUID):
        justification (str):
        valid_until (datetime.date | None):
        requested_by (User):
        decision (DecisionStatus):
        created_on (datetime.datetime):
        requested_on (datetime.datetime):
        decision_note (None | str | Unset):
        decided_by (None | Unset | User):
    """

    id: UUID
    justification: str
    valid_until: datetime.date | None
    requested_by: User
    decision: DecisionStatus
    created_on: datetime.datetime
    requested_on: datetime.datetime
    decision_note: None | str | Unset = UNSET
    decided_by: None | Unset | User = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.user import User

        id = str(self.id)

        justification = self.justification

        valid_until: None | str
        if isinstance(self.valid_until, datetime.date):
            valid_until = self.valid_until.isoformat()
        else:
            valid_until = self.valid_until

        requested_by = self.requested_by.to_dict()

        decision = self.decision.value

        created_on = self.created_on.isoformat()

        requested_on = self.requested_on.isoformat()

        decision_note: None | str | Unset
        if isinstance(self.decision_note, Unset):
            decision_note = UNSET
        else:
            decision_note = self.decision_note

        decided_by: dict[str, Any] | None | Unset
        if isinstance(self.decided_by, Unset):
            decided_by = UNSET
        elif isinstance(self.decided_by, User):
            decided_by = self.decided_by.to_dict()
        else:
            decided_by = self.decided_by

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "justification": justification,
                "valid_until": valid_until,
                "requested_by": requested_by,
                "decision": decision,
                "created_on": created_on,
                "requested_on": requested_on,
            }
        )
        if decision_note is not UNSET:
            field_dict["decision_note"] = decision_note
        if decided_by is not UNSET:
            field_dict["decided_by"] = decided_by

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user import User

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        justification = d.pop("justification")

        def _parse_valid_until(data: object) -> datetime.date | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                valid_until_type_0 = datetime.date.fromisoformat(data)

                return valid_until_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.date | None, data)

        valid_until = _parse_valid_until(d.pop("valid_until"))

        requested_by = User.from_dict(d.pop("requested_by"))

        decision = DecisionStatus(d.pop("decision"))

        created_on = datetime.datetime.fromisoformat(d.pop("created_on"))

        requested_on = datetime.datetime.fromisoformat(d.pop("requested_on"))

        def _parse_decision_note(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        decision_note = _parse_decision_note(d.pop("decision_note", UNSET))

        def _parse_decided_by(data: object) -> None | Unset | User:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                decided_by_type_0 = User.from_dict(data)

                return decided_by_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | User, data)

        decided_by = _parse_decided_by(d.pop("decided_by", UNSET))

        input_port_request_base = cls(
            id=id,
            justification=justification,
            valid_until=valid_until,
            requested_by=requested_by,
            decision=decision,
            created_on=created_on,
            requested_on=requested_on,
            decision_note=decision_note,
            decided_by=decided_by,
        )

        input_port_request_base.additional_properties = d
        return input_port_request_base

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
