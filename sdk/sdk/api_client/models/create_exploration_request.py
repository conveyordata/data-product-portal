from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreateExplorationRequest")


@_attrs_define
class CreateExplorationRequest:
    """
    Attributes:
        name (str):
        namespace (str):
        description (str):
        domain_id (UUID):
    """

    name: str
    namespace: str
    description: str
    domain_id: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        namespace = self.namespace

        description = self.description

        domain_id = str(self.domain_id)

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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        namespace = d.pop("namespace")

        description = d.pop("description")

        domain_id = UUID(d.pop("domain_id"))

        create_exploration_request = cls(
            name=name,
            namespace=namespace,
            description=description,
            domain_id=domain_id,
        )

        create_exploration_request.additional_properties = d
        return create_exploration_request

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
