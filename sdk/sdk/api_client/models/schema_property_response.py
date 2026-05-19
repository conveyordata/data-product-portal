from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SchemaPropertyResponse")


@_attrs_define
class SchemaPropertyResponse:
    """
    Attributes:
        id (UUID):
        name (str):
        position (int):
        business_name (None | str | Unset):
        logical_type (None | str | Unset):
        physical_type (None | str | Unset):
        description (None | str | Unset):
        examples (list[Any] | None | Unset):
        primary_key (bool | Unset):  Default: False.
        primary_key_position (int | None | Unset):
        unique (bool | Unset):  Default: False.
        required (bool | Unset):  Default: False.
        partitioned (bool | Unset):  Default: False.
        partition_key_position (int | None | Unset):
        properties (list[SchemaPropertyResponse] | Unset):
    """

    id: UUID
    name: str
    position: int
    business_name: None | str | Unset = UNSET
    logical_type: None | str | Unset = UNSET
    physical_type: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    examples: list[Any] | None | Unset = UNSET
    primary_key: bool | Unset = False
    primary_key_position: int | None | Unset = UNSET
    unique: bool | Unset = False
    required: bool | Unset = False
    partitioned: bool | Unset = False
    partition_key_position: int | None | Unset = UNSET
    properties: list[SchemaPropertyResponse] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        position = self.position

        business_name: None | str | Unset
        if isinstance(self.business_name, Unset):
            business_name = UNSET
        else:
            business_name = self.business_name

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

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        examples: list[Any] | None | Unset
        if isinstance(self.examples, Unset):
            examples = UNSET
        elif isinstance(self.examples, list):
            examples = self.examples

        else:
            examples = self.examples

        primary_key = self.primary_key

        primary_key_position: int | None | Unset
        if isinstance(self.primary_key_position, Unset):
            primary_key_position = UNSET
        else:
            primary_key_position = self.primary_key_position

        unique = self.unique

        required = self.required

        partitioned = self.partitioned

        partition_key_position: int | None | Unset
        if isinstance(self.partition_key_position, Unset):
            partition_key_position = UNSET
        else:
            partition_key_position = self.partition_key_position

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
                "id": id,
                "name": name,
                "position": position,
            }
        )
        if business_name is not UNSET:
            field_dict["business_name"] = business_name
        if logical_type is not UNSET:
            field_dict["logical_type"] = logical_type
        if physical_type is not UNSET:
            field_dict["physical_type"] = physical_type
        if description is not UNSET:
            field_dict["description"] = description
        if examples is not UNSET:
            field_dict["examples"] = examples
        if primary_key is not UNSET:
            field_dict["primary_key"] = primary_key
        if primary_key_position is not UNSET:
            field_dict["primary_key_position"] = primary_key_position
        if unique is not UNSET:
            field_dict["unique"] = unique
        if required is not UNSET:
            field_dict["required"] = required
        if partitioned is not UNSET:
            field_dict["partitioned"] = partitioned
        if partition_key_position is not UNSET:
            field_dict["partition_key_position"] = partition_key_position
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        position = d.pop("position")

        def _parse_business_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        business_name = _parse_business_name(d.pop("business_name", UNSET))

        def _parse_logical_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        logical_type = _parse_logical_type(d.pop("logical_type", UNSET))

        def _parse_physical_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        physical_type = _parse_physical_type(d.pop("physical_type", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_examples(data: object) -> list[Any] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                examples_type_0 = cast(list[Any], data)

                return examples_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[Any] | None | Unset, data)

        examples = _parse_examples(d.pop("examples", UNSET))

        primary_key = d.pop("primary_key", UNSET)

        def _parse_primary_key_position(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        primary_key_position = _parse_primary_key_position(
            d.pop("primary_key_position", UNSET)
        )

        unique = d.pop("unique", UNSET)

        required = d.pop("required", UNSET)

        partitioned = d.pop("partitioned", UNSET)

        def _parse_partition_key_position(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        partition_key_position = _parse_partition_key_position(
            d.pop("partition_key_position", UNSET)
        )

        _properties = d.pop("properties", UNSET)
        properties: list[SchemaPropertyResponse] | Unset = UNSET
        if _properties is not UNSET:
            properties = []
            for properties_item_data in _properties:
                properties_item = SchemaPropertyResponse.from_dict(properties_item_data)

                properties.append(properties_item)

        schema_property_response = cls(
            id=id,
            name=name,
            position=position,
            business_name=business_name,
            logical_type=logical_type,
            physical_type=physical_type,
            description=description,
            examples=examples,
            primary_key=primary_key,
            primary_key_position=primary_key_position,
            unique=unique,
            required=required,
            partitioned=partitioned,
            partition_key_position=partition_key_position,
            properties=properties,
        )

        schema_property_response.additional_properties = d
        return schema_property_response

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
