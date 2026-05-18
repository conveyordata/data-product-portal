from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_property_request import SchemaPropertyRequest


T = TypeVar("T", bound="SchemaObjectRequest")


@_attrs_define
class SchemaObjectRequest:
    """
    Attributes:
        name (str):
        logical_type (None | str | Unset):
        physical_type (None | str | Unset):
        physical_name (None | str | Unset):
        description (None | str | Unset):
        properties (list[SchemaPropertyRequest] | Unset):
    """

    name: str
    logical_type: None | str | Unset = UNSET
    physical_type: None | str | Unset = UNSET
    physical_name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    properties: list[SchemaPropertyRequest] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        logical_type: None | str | Unset
        if isinstance(self.logical_type, Unset):
            logical_type = UNSET
        else:
            logical_type = self.logical_type

        physical_type: None | str | Unset
        if isinstance(self.physical_type, Unset):
            physical_type = UNSET
        else:
            physical_type = self.physical_type

        physical_name: None | str | Unset
        if isinstance(self.physical_name, Unset):
            physical_name = UNSET
        else:
            physical_name = self.physical_name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        properties: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.properties, Unset):
            properties = []
            for properties_item_data in self.properties:
                properties_item = properties_item_data.to_dict()
                properties.append(properties_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if logical_type is not UNSET:
            field_dict["logicalType"] = logical_type
        if physical_type is not UNSET:
            field_dict["physicalType"] = physical_type
        if physical_name is not UNSET:
            field_dict["physicalName"] = physical_name
        if description is not UNSET:
            field_dict["description"] = description
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_property_request import SchemaPropertyRequest

        d = dict(src_dict)
        name = d.pop("name")

        def _parse_logical_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        logical_type = _parse_logical_type(d.pop("logicalType", UNSET))

        def _parse_physical_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        physical_type = _parse_physical_type(d.pop("physicalType", UNSET))

        def _parse_physical_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        physical_name = _parse_physical_name(d.pop("physicalName", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        _properties = d.pop("properties", UNSET)
        properties: list[SchemaPropertyRequest] | Unset = UNSET
        if _properties is not UNSET:
            properties = []
            for properties_item_data in _properties:
                properties_item = SchemaPropertyRequest.from_dict(properties_item_data)

                properties.append(properties_item)

        schema_object_request = cls(
            name=name,
            logical_type=logical_type,
            physical_type=physical_type,
            physical_name=physical_name,
            description=description,
            properties=properties,
        )

        schema_object_request.additional_properties = d
        return schema_object_request

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
