from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SchemaRelationshipResponse")


@_attrs_define
class SchemaRelationshipResponse:
    """
    Attributes:
        id (UUID):
        type_ (str):
        source_object_id (UUID):
        source_property_id (UUID):
        target_object_id (UUID):
        target_property_id (UUID):
    """

    id: UUID
    type_: str
    source_object_id: UUID
    source_property_id: UUID
    target_object_id: UUID
    target_property_id: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        type_ = self.type_

        source_object_id = str(self.source_object_id)

        source_property_id = str(self.source_property_id)

        target_object_id = str(self.target_object_id)

        target_property_id = str(self.target_property_id)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "type": type_,
                "source_object_id": source_object_id,
                "source_property_id": source_property_id,
                "target_object_id": target_object_id,
                "target_property_id": target_property_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        type_ = d.pop("type")

        source_object_id = UUID(d.pop("source_object_id"))

        source_property_id = UUID(d.pop("source_property_id"))

        target_object_id = UUID(d.pop("target_object_id"))

        target_property_id = UUID(d.pop("target_property_id"))

        schema_relationship_response = cls(
            id=id,
            type_=type_,
            source_object_id=source_object_id,
            source_property_id=source_property_id,
            target_object_id=target_object_id,
            target_property_id=target_property_id,
        )

        schema_relationship_response.additional_properties = d
        return schema_relationship_response

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
