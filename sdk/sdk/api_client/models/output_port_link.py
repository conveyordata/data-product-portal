from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.decision_status import DecisionStatus

if TYPE_CHECKING:
    from ..models.output_port import OutputPort


T = TypeVar("T", bound="OutputPortLink")


@_attrs_define
class OutputPortLink:
    """
    Attributes:
        id (UUID):
        output_port_id (UUID):
        technical_asset_id (UUID):
        status (DecisionStatus):
        output (OutputPort):
    """

    id: UUID
    output_port_id: UUID
    technical_asset_id: UUID
    status: DecisionStatus
    output: OutputPort
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        output_port_id = str(self.output_port_id)

        technical_asset_id = str(self.technical_asset_id)

        status = self.status.value

        output = self.output.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "output_port_id": output_port_id,
                "technical_asset_id": technical_asset_id,
                "status": status,
                "output": output,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.output_port import OutputPort

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        output_port_id = UUID(d.pop("output_port_id"))

        technical_asset_id = UUID(d.pop("technical_asset_id"))

        status = DecisionStatus(d.pop("status"))

        output = OutputPort.from_dict(d.pop("output"))

        output_port_link = cls(
            id=id,
            output_port_id=output_port_id,
            technical_asset_id=technical_asset_id,
            status=status,
            output=output,
        )

        output_port_link.additional_properties = d
        return output_port_link

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
