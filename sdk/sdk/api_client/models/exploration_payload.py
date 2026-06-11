from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ExplorationPayload")


@_attrs_define
class ExplorationPayload:
    """
    Attributes:
        id (UUID):
        name (str):
        namespace (str):
        description (None | str):
        domain_id (UUID):
        owner_id (UUID):
    """

    id: UUID
    name: str
    namespace: str
    description: None | str
    domain_id: UUID
    owner_id: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        namespace = self.namespace

        description: None | str
        description = self.description

        domain_id = str(self.domain_id)

        owner_id = str(self.owner_id)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "namespace": namespace,
                "description": description,
                "domain_id": domain_id,
                "owner_id": owner_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        namespace = d.pop("namespace")

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        domain_id = UUID(d.pop("domain_id"))

        owner_id = UUID(d.pop("owner_id"))

        exploration_payload = cls(
            id=id,
            name=name,
            namespace=namespace,
            description=description,
            domain_id=domain_id,
            owner_id=owner_id,
        )

        exploration_payload.additional_properties = d
        return exploration_payload

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
