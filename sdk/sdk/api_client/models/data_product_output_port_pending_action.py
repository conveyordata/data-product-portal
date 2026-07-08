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
    from ..models.abstract_data_product_info import AbstractDataProductInfo
    from ..models.output_port import OutputPort
    from ..models.user import User


T = TypeVar("T", bound="DataProductOutputPortPendingAction")


@_attrs_define
class DataProductOutputPortPendingAction:
    """
    Attributes:
        id (UUID):
        justification (str):
        consuming_abstract_data_product_id (UUID):
        output_port_id (UUID):
        status (DecisionStatus):
        requested_on (datetime.datetime):
        output_port (OutputPort):
        consuming_abstract_data_product (AbstractDataProductInfo):
        requested_by (User):
        denied_by (None | User):
        approved_by (None | User):
        requested_duration_days (int | None | Unset):
        expires_on (datetime.datetime | None | Unset):
        is_expiring_soon (bool | Unset):  Default: False.
        renewed_on (datetime.datetime | None | Unset):
        total_range_start (datetime.datetime | None | Unset):
        total_range_end (datetime.datetime | None | Unset):
        pending_action_type (Literal['InputPort'] | Unset):  Default: 'InputPort'.
    """

    id: UUID
    justification: str
    consuming_abstract_data_product_id: UUID
    output_port_id: UUID
    status: DecisionStatus
    requested_on: datetime.datetime
    output_port: OutputPort
    consuming_abstract_data_product: AbstractDataProductInfo
    requested_by: User
    denied_by: None | User
    approved_by: None | User
    requested_duration_days: int | None | Unset = UNSET
    expires_on: datetime.datetime | None | Unset = UNSET
    is_expiring_soon: bool | Unset = False
    renewed_on: datetime.datetime | None | Unset = UNSET
    total_range_start: datetime.datetime | None | Unset = UNSET
    total_range_end: datetime.datetime | None | Unset = UNSET
    pending_action_type: Literal["InputPort"] | Unset = "InputPort"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.user import User

        id = str(self.id)

        justification = self.justification

        consuming_abstract_data_product_id = str(
            self.consuming_abstract_data_product_id
        )

        output_port_id = str(self.output_port_id)

        status = self.status.value

        requested_on = self.requested_on.isoformat()

        output_port = self.output_port.to_dict()

        consuming_abstract_data_product = self.consuming_abstract_data_product.to_dict()

        requested_by = self.requested_by.to_dict()

        denied_by: dict[str, Any] | None
        if isinstance(self.denied_by, User):
            denied_by = self.denied_by.to_dict()
        else:
            denied_by = self.denied_by

        approved_by: dict[str, Any] | None
        if isinstance(self.approved_by, User):
            approved_by = self.approved_by.to_dict()
        else:
            approved_by = self.approved_by

        requested_duration_days: int | None | Unset
        if isinstance(self.requested_duration_days, Unset):
            requested_duration_days = UNSET
        else:
            requested_duration_days = self.requested_duration_days

        expires_on: None | str | Unset
        if isinstance(self.expires_on, Unset):
            expires_on = UNSET
        elif isinstance(self.expires_on, datetime.datetime):
            expires_on = self.expires_on.isoformat()
        else:
            expires_on = self.expires_on

        is_expiring_soon = self.is_expiring_soon

        renewed_on: None | str | Unset
        if isinstance(self.renewed_on, Unset):
            renewed_on = UNSET
        elif isinstance(self.renewed_on, datetime.datetime):
            renewed_on = self.renewed_on.isoformat()
        else:
            renewed_on = self.renewed_on

        total_range_start: None | str | Unset
        if isinstance(self.total_range_start, Unset):
            total_range_start = UNSET
        elif isinstance(self.total_range_start, datetime.datetime):
            total_range_start = self.total_range_start.isoformat()
        else:
            total_range_start = self.total_range_start

        total_range_end: None | str | Unset
        if isinstance(self.total_range_end, Unset):
            total_range_end = UNSET
        elif isinstance(self.total_range_end, datetime.datetime):
            total_range_end = self.total_range_end.isoformat()
        else:
            total_range_end = self.total_range_end

        pending_action_type = self.pending_action_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "justification": justification,
                "consuming_abstract_data_product_id": consuming_abstract_data_product_id,
                "output_port_id": output_port_id,
                "status": status,
                "requested_on": requested_on,
                "output_port": output_port,
                "consuming_abstract_data_product": consuming_abstract_data_product,
                "requested_by": requested_by,
                "denied_by": denied_by,
                "approved_by": approved_by,
            }
        )
        if requested_duration_days is not UNSET:
            field_dict["requested_duration_days"] = requested_duration_days
        if expires_on is not UNSET:
            field_dict["expires_on"] = expires_on
        if is_expiring_soon is not UNSET:
            field_dict["is_expiring_soon"] = is_expiring_soon
        if renewed_on is not UNSET:
            field_dict["renewed_on"] = renewed_on
        if total_range_start is not UNSET:
            field_dict["total_range_start"] = total_range_start
        if total_range_end is not UNSET:
            field_dict["total_range_end"] = total_range_end
        if pending_action_type is not UNSET:
            field_dict["pending_action_type"] = pending_action_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.abstract_data_product_info import AbstractDataProductInfo
        from ..models.output_port import OutputPort
        from ..models.user import User

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        justification = d.pop("justification")

        consuming_abstract_data_product_id = UUID(
            d.pop("consuming_abstract_data_product_id")
        )

        output_port_id = UUID(d.pop("output_port_id"))

        status = DecisionStatus(d.pop("status"))

        requested_on = datetime.datetime.fromisoformat(d.pop("requested_on"))

        output_port = OutputPort.from_dict(d.pop("output_port"))

        consuming_abstract_data_product = AbstractDataProductInfo.from_dict(
            d.pop("consuming_abstract_data_product")
        )

        requested_by = User.from_dict(d.pop("requested_by"))

        def _parse_denied_by(data: object) -> None | User:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                denied_by_type_0 = User.from_dict(data)

                return denied_by_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | User, data)

        denied_by = _parse_denied_by(d.pop("denied_by"))

        def _parse_approved_by(data: object) -> None | User:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                approved_by_type_0 = User.from_dict(data)

                return approved_by_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | User, data)

        approved_by = _parse_approved_by(d.pop("approved_by"))

        def _parse_requested_duration_days(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        requested_duration_days = _parse_requested_duration_days(
            d.pop("requested_duration_days", UNSET)
        )

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

        is_expiring_soon = d.pop("is_expiring_soon", UNSET)

        def _parse_renewed_on(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                renewed_on_type_0 = datetime.datetime.fromisoformat(data)

                return renewed_on_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        renewed_on = _parse_renewed_on(d.pop("renewed_on", UNSET))

        def _parse_total_range_start(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                total_range_start_type_0 = datetime.datetime.fromisoformat(data)

                return total_range_start_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        total_range_start = _parse_total_range_start(d.pop("total_range_start", UNSET))

        def _parse_total_range_end(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                total_range_end_type_0 = datetime.datetime.fromisoformat(data)

                return total_range_end_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        total_range_end = _parse_total_range_end(d.pop("total_range_end", UNSET))

        pending_action_type = cast(
            Literal["InputPort"] | Unset, d.pop("pending_action_type", UNSET)
        )
        if pending_action_type != "InputPort" and not isinstance(
            pending_action_type, Unset
        ):
            raise ValueError(
                f"pending_action_type must match const 'InputPort', got '{pending_action_type}'"
            )

        data_product_output_port_pending_action = cls(
            id=id,
            justification=justification,
            consuming_abstract_data_product_id=consuming_abstract_data_product_id,
            output_port_id=output_port_id,
            status=status,
            requested_on=requested_on,
            output_port=output_port,
            consuming_abstract_data_product=consuming_abstract_data_product,
            requested_by=requested_by,
            denied_by=denied_by,
            approved_by=approved_by,
            requested_duration_days=requested_duration_days,
            expires_on=expires_on,
            is_expiring_soon=is_expiring_soon,
            renewed_on=renewed_on,
            total_range_start=total_range_start,
            total_range_end=total_range_end,
            pending_action_type=pending_action_type,
        )

        data_product_output_port_pending_action.additional_properties = d
        return data_product_output_port_pending_action

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
