from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_object_response import SchemaObjectResponse
    from ..models.schema_relationship_response import SchemaRelationshipResponse


T = TypeVar("T", bound="OutputPortSchemaResponse")


@_attrs_define
class OutputPortSchemaResponse:
    """
    Attributes:
        output_port_id (UUID):
        schema_objects (list[SchemaObjectResponse] | Unset):
        relationships (list[SchemaRelationshipResponse] | Unset):
    """

    output_port_id: UUID
    schema_objects: list[SchemaObjectResponse] | Unset = UNSET
    relationships: list[SchemaRelationshipResponse] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        output_port_id = str(self.output_port_id)

        schema_objects: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.schema_objects, Unset):
            schema_objects = []
            for schema_objects_item_data in self.schema_objects:
                schema_objects_item = schema_objects_item_data.to_dict()
                schema_objects.append(schema_objects_item)

        relationships: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.relationships, Unset):
            relationships = []
            for relationships_item_data in self.relationships:
                relationships_item = relationships_item_data.to_dict()
                relationships.append(relationships_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "output_port_id": output_port_id,
            }
        )
        if schema_objects is not UNSET:
            field_dict["schema_objects"] = schema_objects
        if relationships is not UNSET:
            field_dict["relationships"] = relationships

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_object_response import SchemaObjectResponse
        from ..models.schema_relationship_response import SchemaRelationshipResponse

        d = dict(src_dict)
        output_port_id = UUID(d.pop("output_port_id"))

        _schema_objects = d.pop("schema_objects", UNSET)
        schema_objects: list[SchemaObjectResponse] | Unset = UNSET
        if _schema_objects is not UNSET:
            schema_objects = []
            for schema_objects_item_data in _schema_objects:
                schema_objects_item = SchemaObjectResponse.from_dict(
                    schema_objects_item_data
                )

                schema_objects.append(schema_objects_item)

        _relationships = d.pop("relationships", UNSET)
        relationships: list[SchemaRelationshipResponse] | Unset = UNSET
        if _relationships is not UNSET:
            relationships = []
            for relationships_item_data in _relationships:
                relationships_item = SchemaRelationshipResponse.from_dict(
                    relationships_item_data
                )

                relationships.append(relationships_item)

        output_port_schema_response = cls(
            output_port_id=output_port_id,
            schema_objects=schema_objects,
            relationships=relationships,
        )

        output_port_schema_response.additional_properties = d
        return output_port_schema_response

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
