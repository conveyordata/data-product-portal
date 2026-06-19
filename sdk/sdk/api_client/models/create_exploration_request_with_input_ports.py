from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.request_input_ports_for_exploration_request import (
        RequestInputPortsForExplorationRequest,
    )


T = TypeVar("T", bound="CreateExplorationRequestWithInputPorts")


@_attrs_define
class CreateExplorationRequestWithInputPorts:
    """
    Attributes:
        name (str):
        namespace (str):
        description (str):
        domain_id (UUID):
        input_ports (None | RequestInputPortsForExplorationRequest | Unset):
    """

    name: str
    namespace: str
    description: str
    domain_id: UUID
    input_ports: None | RequestInputPortsForExplorationRequest | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.request_input_ports_for_exploration_request import (
            RequestInputPortsForExplorationRequest,
        )

        name = self.name

        namespace = self.namespace

        description = self.description

        domain_id = str(self.domain_id)

        input_ports: dict[str, Any] | None | Unset
        if isinstance(self.input_ports, Unset):
            input_ports = UNSET
        elif isinstance(self.input_ports, RequestInputPortsForExplorationRequest):
            input_ports = self.input_ports.to_dict()
        else:
            input_ports = self.input_ports

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "namespace": namespace,
                "description": description,
                "domain_id": domain_id,
            }
        )
        if input_ports is not UNSET:
            field_dict["input_ports"] = input_ports

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.request_input_ports_for_exploration_request import (
            RequestInputPortsForExplorationRequest,
        )

        d = dict(src_dict)
        name = d.pop("name")

        namespace = d.pop("namespace")

        description = d.pop("description")

        domain_id = UUID(d.pop("domain_id"))

        def _parse_input_ports(
            data: object,
        ) -> None | RequestInputPortsForExplorationRequest | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                input_ports_type_0 = RequestInputPortsForExplorationRequest.from_dict(
                    data
                )

                return input_ports_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RequestInputPortsForExplorationRequest | Unset, data)

        input_ports = _parse_input_ports(d.pop("input_ports", UNSET))

        create_exploration_request_with_input_ports = cls(
            name=name,
            namespace=namespace,
            description=description,
            domain_id=domain_id,
            input_ports=input_ports,
        )

        create_exploration_request_with_input_ports.additional_properties = d
        return create_exploration_request_with_input_ports

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
