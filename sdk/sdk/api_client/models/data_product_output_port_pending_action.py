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
from dateutil.parser import isoparse

from ..models.decision_status import DecisionStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.data_product import DataProduct
    from ..models.output_port import OutputPort
    from ..models.user import User


T = TypeVar("T", bound="DataProductOutputPortPendingAction")


@_attrs_define
class DataProductOutputPortPendingAction:
    """
    Attributes:
        id (UUID):
        justification (str):
        data_product_id (UUID):
        output_port_id (UUID):
        status (DecisionStatus):
        requested_on (datetime.datetime):
        output_port (OutputPort):
        data_product (DataProduct):
        requested_by (User):
        denied_by (None | User):
        approved_by (None | User):
        pending_action_type (Literal['DataProductOutputPort'] | Unset):  Default: 'DataProductOutputPort'.
    """

    id: UUID
    justification: str
    data_product_id: UUID
    output_port_id: UUID
    status: DecisionStatus
    requested_on: datetime.datetime
    output_port: OutputPort
    data_product: DataProduct
    requested_by: User
    denied_by: None | User
    approved_by: None | User
    pending_action_type: Literal["DataProductOutputPort"] | Unset = (
        "DataProductOutputPort"
    )
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.user import User

        id = str(self.id)

        justification = self.justification

        data_product_id = str(self.data_product_id)

        output_port_id = str(self.output_port_id)

        status = self.status.value

        requested_on = self.requested_on.isoformat()

        output_port = self.output_port.to_dict()

        data_product = self.data_product.to_dict()

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

        pending_action_type = self.pending_action_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "justification": justification,
                "data_product_id": data_product_id,
                "output_port_id": output_port_id,
                "status": status,
                "requested_on": requested_on,
                "output_port": output_port,
                "data_product": data_product,
                "requested_by": requested_by,
                "denied_by": denied_by,
                "approved_by": approved_by,
            }
        )
        if pending_action_type is not UNSET:
            field_dict["pending_action_type"] = pending_action_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_product import DataProduct
        from ..models.output_port import OutputPort
        from ..models.user import User

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        justification = d.pop("justification")

        data_product_id = UUID(d.pop("data_product_id"))

        output_port_id = UUID(d.pop("output_port_id"))

        status = DecisionStatus(d.pop("status"))

        requested_on = isoparse(d.pop("requested_on"))

        output_port = OutputPort.from_dict(d.pop("output_port"))

        data_product = DataProduct.from_dict(d.pop("data_product"))

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

        pending_action_type = cast(
            Literal["DataProductOutputPort"] | Unset,
            d.pop("pending_action_type", UNSET),
        )
        if pending_action_type != "DataProductOutputPort" and not isinstance(
            pending_action_type, Unset
        ):
            raise ValueError(
                f"pending_action_type must match const 'DataProductOutputPort', got '{pending_action_type}'"
            )

        data_product_output_port_pending_action = cls(
            id=id,
            justification=justification,
            data_product_id=data_product_id,
            output_port_id=output_port_id,
            status=status,
            requested_on=requested_on,
            output_port=output_port,
            data_product=data_product,
            requested_by=requested_by,
            denied_by=denied_by,
            approved_by=approved_by,
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
