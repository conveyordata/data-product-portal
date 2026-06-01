from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.decision_status import DecisionStatus

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
    """

    id: UUID
    justification: str
    status: DecisionStatus
    output_port_id: UUID
    output_port: OutputPort
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        justification = self.justification

        status = self.status.value

        output_port_id = str(self.output_port_id)

        output_port = self.output_port.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "justification": justification,
                "status": status,
                "output_port_id": output_port_id,
                "output_port": output_port,
            }
        )

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

        input_port = cls(
            id=id,
            justification=justification,
            status=status,
            output_port_id=output_port_id,
            output_port=output_port,
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
