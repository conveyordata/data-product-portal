from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_object_request import SchemaObjectRequest


T = TypeVar("T", bound="BitolContractRequest")


@_attrs_define
class BitolContractRequest:
    """Accepts a BitOL data contract (https://bitol-io.github.io/open-data-contract-standard/).
    Only the `schema` section is extracted; all other fields are ignored.

        Attributes:
            schema (list[SchemaObjectRequest] | Unset):
    """

    schema: list[SchemaObjectRequest] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        schema: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.schema, Unset):
            schema = []
            for schema_item_data in self.schema:
                schema_item = schema_item_data.to_dict()
                schema.append(schema_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if schema is not UNSET:
            field_dict["schema"] = schema

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_object_request import SchemaObjectRequest

        d = dict(src_dict)
        _schema = d.pop("schema", UNSET)
        schema: list[SchemaObjectRequest] | Unset = UNSET
        if _schema is not UNSET:
            schema = []
            for schema_item_data in _schema:
                schema_item = SchemaObjectRequest.from_dict(schema_item_data)

                schema.append(schema_item)

        bitol_contract_request = cls(
            schema=schema,
        )

        bitol_contract_request.additional_properties = d
        return bitol_contract_request

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
