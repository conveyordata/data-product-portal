from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.decision_status import DecisionStatus

if TYPE_CHECKING:
    from ..models.output_port import OutputPort
    from ..models.role import Role
    from ..models.user import User


T = TypeVar("T", bound="OutputPortRoleAssignmentResponse")


@_attrs_define
class OutputPortRoleAssignmentResponse:
    """
    Attributes:
        id (UUID):
        output_port (OutputPort):
        user (User):
        role (None | Role):
        decision (DecisionStatus):
        requested_on (datetime.datetime | None):
        requested_by (None | User):
        decided_on (datetime.datetime | None):
        decided_by (None | User):
    """

    id: UUID
    output_port: OutputPort
    user: User
    role: None | Role
    decision: DecisionStatus
    requested_on: datetime.datetime | None
    requested_by: None | User
    decided_on: datetime.datetime | None
    decided_by: None | User
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.role import Role
        from ..models.user import User

        id = str(self.id)

        output_port = self.output_port.to_dict()

        user = self.user.to_dict()

        role: dict[str, Any] | None
        if isinstance(self.role, Role):
            role = self.role.to_dict()
        else:
            role = self.role

        decision = self.decision.value

        requested_on: None | str
        if isinstance(self.requested_on, datetime.datetime):
            requested_on = self.requested_on.isoformat()
        else:
            requested_on = self.requested_on

        requested_by: dict[str, Any] | None
        if isinstance(self.requested_by, User):
            requested_by = self.requested_by.to_dict()
        else:
            requested_by = self.requested_by

        decided_on: None | str
        if isinstance(self.decided_on, datetime.datetime):
            decided_on = self.decided_on.isoformat()
        else:
            decided_on = self.decided_on

        decided_by: dict[str, Any] | None
        if isinstance(self.decided_by, User):
            decided_by = self.decided_by.to_dict()
        else:
            decided_by = self.decided_by

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "output_port": output_port,
                "user": user,
                "role": role,
                "decision": decision,
                "requested_on": requested_on,
                "requested_by": requested_by,
                "decided_on": decided_on,
                "decided_by": decided_by,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.output_port import OutputPort
        from ..models.role import Role
        from ..models.user import User

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        output_port = OutputPort.from_dict(d.pop("output_port"))

        user = User.from_dict(d.pop("user"))

        def _parse_role(data: object) -> None | Role:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                role_type_0 = Role.from_dict(data)

                return role_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Role, data)

        role = _parse_role(d.pop("role"))

        decision = DecisionStatus(d.pop("decision"))

        def _parse_requested_on(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                requested_on_type_0 = isoparse(data)

                return requested_on_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        requested_on = _parse_requested_on(d.pop("requested_on"))

        def _parse_requested_by(data: object) -> None | User:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                requested_by_type_0 = User.from_dict(data)

                return requested_by_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | User, data)

        requested_by = _parse_requested_by(d.pop("requested_by"))

        def _parse_decided_on(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                decided_on_type_0 = isoparse(data)

                return decided_on_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        decided_on = _parse_decided_on(d.pop("decided_on"))

        def _parse_decided_by(data: object) -> None | User:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                decided_by_type_0 = User.from_dict(data)

                return decided_by_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | User, data)

        decided_by = _parse_decided_by(d.pop("decided_by"))

        output_port_role_assignment_response = cls(
            id=id,
            output_port=output_port,
            user=user,
            role=role,
            decision=decision,
            requested_on=requested_on,
            requested_by=requested_by,
            decided_on=decided_on,
            decided_by=decided_by,
        )

        output_port_role_assignment_response.additional_properties = d
        return output_port_role_assignment_response

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
