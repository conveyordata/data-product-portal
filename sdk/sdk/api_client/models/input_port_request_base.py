from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.access_duration_type import AccessDurationType
from ..models.input_port_request_decision import InputPortRequestDecision
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
        access_duration_type (AccessDurationType):
        requested_by (User):
        decision (InputPortRequestDecision):
        created_on (datetime.datetime):
        requested_on (datetime.datetime):
        decision_note (None | str | Unset):
        valid_from (datetime.date | None | Unset):
        requested_duration_days (int | None | Unset):
        decided_by (None | Unset | User):
        revoked_at (datetime.datetime | None | Unset):
        revoked_by (None | Unset | User):
    """

    id: UUID
    justification: str
    valid_until: datetime.date | None
    access_duration_type: AccessDurationType
    requested_by: User
    decision: InputPortRequestDecision
    created_on: datetime.datetime
    requested_on: datetime.datetime
    decision_note: None | str | Unset = UNSET
    valid_from: datetime.date | None | Unset = UNSET
    requested_duration_days: int | None | Unset = UNSET
    decided_by: None | Unset | User = UNSET
    revoked_at: datetime.datetime | None | Unset = UNSET
    revoked_by: None | Unset | User = UNSET
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

        access_duration_type = self.access_duration_type.value

        requested_by = self.requested_by.to_dict()

        decision = self.decision.value

        created_on = self.created_on.isoformat()

        requested_on = self.requested_on.isoformat()

        decision_note: None | str | Unset
        if isinstance(self.decision_note, Unset):
            decision_note = UNSET
        else:
            decision_note = self.decision_note

        valid_from: None | str | Unset
        if isinstance(self.valid_from, Unset):
            valid_from = UNSET
        elif isinstance(self.valid_from, datetime.date):
            valid_from = self.valid_from.isoformat()
        else:
            valid_from = self.valid_from

        requested_duration_days: int | None | Unset
        if isinstance(self.requested_duration_days, Unset):
            requested_duration_days = UNSET
        else:
            requested_duration_days = self.requested_duration_days

        decided_by: dict[str, Any] | None | Unset
        if isinstance(self.decided_by, Unset):
            decided_by = UNSET
        elif isinstance(self.decided_by, User):
            decided_by = self.decided_by.to_dict()
        else:
            decided_by = self.decided_by

        revoked_at: None | str | Unset
        if isinstance(self.revoked_at, Unset):
            revoked_at = UNSET
        elif isinstance(self.revoked_at, datetime.datetime):
            revoked_at = self.revoked_at.isoformat()
        else:
            revoked_at = self.revoked_at

        revoked_by: dict[str, Any] | None | Unset
        if isinstance(self.revoked_by, Unset):
            revoked_by = UNSET
        elif isinstance(self.revoked_by, User):
            revoked_by = self.revoked_by.to_dict()
        else:
            revoked_by = self.revoked_by

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "justification": justification,
                "valid_until": valid_until,
                "access_duration_type": access_duration_type,
                "requested_by": requested_by,
                "decision": decision,
                "created_on": created_on,
                "requested_on": requested_on,
            }
        )
        if decision_note is not UNSET:
            field_dict["decision_note"] = decision_note
        if valid_from is not UNSET:
            field_dict["valid_from"] = valid_from
        if requested_duration_days is not UNSET:
            field_dict["requested_duration_days"] = requested_duration_days
        if decided_by is not UNSET:
            field_dict["decided_by"] = decided_by
        if revoked_at is not UNSET:
            field_dict["revoked_at"] = revoked_at
        if revoked_by is not UNSET:
            field_dict["revoked_by"] = revoked_by

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

        access_duration_type = AccessDurationType(d.pop("access_duration_type"))

        requested_by = User.from_dict(d.pop("requested_by"))

        decision = InputPortRequestDecision(d.pop("decision"))

        created_on = datetime.datetime.fromisoformat(d.pop("created_on"))

        requested_on = datetime.datetime.fromisoformat(d.pop("requested_on"))

        def _parse_decision_note(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        decision_note = _parse_decision_note(d.pop("decision_note", UNSET))

        def _parse_valid_from(data: object) -> datetime.date | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                valid_from_type_0 = datetime.date.fromisoformat(data)

                return valid_from_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.date | None | Unset, data)

        valid_from = _parse_valid_from(d.pop("valid_from", UNSET))

        def _parse_requested_duration_days(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        requested_duration_days = _parse_requested_duration_days(
            d.pop("requested_duration_days", UNSET)
        )

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

        def _parse_revoked_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                revoked_at_type_0 = datetime.datetime.fromisoformat(data)

                return revoked_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        revoked_at = _parse_revoked_at(d.pop("revoked_at", UNSET))

        def _parse_revoked_by(data: object) -> None | Unset | User:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                revoked_by_type_0 = User.from_dict(data)

                return revoked_by_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | User, data)

        revoked_by = _parse_revoked_by(d.pop("revoked_by", UNSET))

        input_port_request_base = cls(
            id=id,
            justification=justification,
            valid_until=valid_until,
            access_duration_type=access_duration_type,
            requested_by=requested_by,
            decision=decision,
            created_on=created_on,
            requested_on=requested_on,
            decision_note=decision_note,
            valid_from=valid_from,
            requested_duration_days=requested_duration_days,
            decided_by=decided_by,
            revoked_at=revoked_at,
            revoked_by=revoked_by,
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
