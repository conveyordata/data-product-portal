from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.identity_batch_create_error import IdentityBatchCreateError


T = TypeVar("T", bound="IdentityBatchCreateResponse")


@_attrs_define
class IdentityBatchCreateResponse:
    """
    Attributes:
        ids (list[UUID]):
        errors (list[IdentityBatchCreateError]):
    """

    ids: list[UUID]
    errors: list[IdentityBatchCreateError]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ids = []
        for ids_item_data in self.ids:
            ids_item = str(ids_item_data)
            ids.append(ids_item)

        errors = []
        for errors_item_data in self.errors:
            errors_item = errors_item_data.to_dict()
            errors.append(errors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ids": ids,
                "errors": errors,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.identity_batch_create_error import (
            IdentityBatchCreateError,  # noqa: PLC0415
        )

        d = dict(src_dict)
        ids = []
        _ids = d.pop("ids")
        for ids_item_data in _ids:
            ids_item = UUID(ids_item_data)

            ids.append(ids_item)

        errors = []
        _errors = d.pop("errors")
        for errors_item_data in _errors:
            errors_item = IdentityBatchCreateError.from_dict(errors_item_data)

            errors.append(errors_item)

        identity_batch_create_response = cls(
            ids=ids,
            errors=errors,
        )

        identity_batch_create_response.additional_properties = d
        return identity_batch_create_response

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
