from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    TypeVar,
    cast,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.decision_status import DecisionStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user import User
    from ..models.user_input_port import UserInputPort


T = TypeVar("T", bound="InputPortRequest")


@_attrs_define
class InputPortRequest:
    """
    Attributes:
        id (UUID):
        justification (str):
        valid_until (datetime.datetime | None):
        requested_by (User):
        decision (DecisionStatus):
        created_on (datetime.datetime):
        requested_on (datetime.datetime):
        input_port (UserInputPort):
        decision_note (None | str | Unset):
        decided_by (None | Unset | User):
        request_type (Literal['InputPort'] | Unset):  Default: 'InputPort'.
    """

    id: UUID
    justification: str
    valid_until: datetime.datetime | None
    requested_by: User
    decision: DecisionStatus
    created_on: datetime.datetime
    requested_on: datetime.datetime
    input_port: UserInputPort
    decision_note: None | str | Unset = UNSET
    decided_by: None | Unset | User = UNSET
    request_type: Literal["InputPort"] | Unset = "InputPort"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.user import User

        id = str(self.id)

        justification = self.justification

        valid_until: None | str
        if isinstance(self.valid_until, datetime.datetime):
            valid_until = self.valid_until.isoformat()
        else:
            valid_until = self.valid_until

        requested_by = self.requested_by.to_dict()

        decision = self.decision.value

        created_on = self.created_on.isoformat()

        requested_on = self.requested_on.isoformat()

        input_port = self.input_port.to_dict()

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

        request_type = self.request_type

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
                "input_port": input_port,
            }
        )
        if decision_note is not UNSET:
            field_dict["decision_note"] = decision_note
        if decided_by is not UNSET:
            field_dict["decided_by"] = decided_by
        if request_type is not UNSET:
            field_dict["request_type"] = request_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user import User
        from ..models.user_input_port import UserInputPort

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        justification = d.pop("justification")

        def _parse_valid_until(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                valid_until_type_0 = datetime.datetime.fromisoformat(data)

                return valid_until_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        valid_until = _parse_valid_until(d.pop("valid_until"))

        requested_by = User.from_dict(d.pop("requested_by"))

        decision = DecisionStatus(d.pop("decision"))

        created_on = datetime.datetime.fromisoformat(d.pop("created_on"))

        requested_on = datetime.datetime.fromisoformat(d.pop("requested_on"))

        input_port = UserInputPort.from_dict(d.pop("input_port"))

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

        request_type = cast(Literal["InputPort"] | Unset, d.pop("request_type", UNSET))
        if request_type != "InputPort" and not isinstance(request_type, Unset):
            raise ValueError(
                f"request_type must match const 'InputPort', got '{request_type}'"
            )

        input_port_request = cls(
            id=id,
            justification=justification,
            valid_until=valid_until,
            requested_by=requested_by,
            decision=decision,
            created_on=created_on,
            requested_on=requested_on,
            input_port=input_port,
            decision_note=decision_note,
            decided_by=decided_by,
            request_type=request_type,
        )

        input_port_request.additional_properties = d
        return input_port_request

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
