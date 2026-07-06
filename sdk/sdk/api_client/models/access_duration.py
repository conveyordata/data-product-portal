from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.abstract_data_product_type import AbstractDataProductType
from ..models.access_duration_type import AccessDurationType

T = TypeVar("T", bound="AccessDuration")


@_attrs_define
class AccessDuration:
    """
    Attributes:
        id (UUID):
        abstract_data_product_type (AbstractDataProductType):
        access_duration_type (AccessDurationType):
        days (int | None):
        is_default (bool):
    """

    id: UUID
    abstract_data_product_type: AbstractDataProductType
    access_duration_type: AccessDurationType
    days: int | None
    is_default: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        abstract_data_product_type = self.abstract_data_product_type.value

        access_duration_type = self.access_duration_type.value

        days: int | None
        days = self.days

        is_default = self.is_default

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "abstract_data_product_type": abstract_data_product_type,
                "access_duration_type": access_duration_type,
                "days": days,
                "is_default": is_default,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        abstract_data_product_type = AbstractDataProductType(
            d.pop("abstract_data_product_type")
        )

        access_duration_type = AccessDurationType(d.pop("access_duration_type"))

        def _parse_days(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        days = _parse_days(d.pop("days"))

        is_default = d.pop("is_default")

        access_duration = cls(
            id=id,
            abstract_data_product_type=abstract_data_product_type,
            access_duration_type=access_duration_type,
            days=days,
            is_default=is_default,
        )

        access_duration.additional_properties = d
        return access_duration

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
