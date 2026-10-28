from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.environment_get_item import EnvironmentGetItem


T = TypeVar("T", bound="DataProductEnvironment")


@_attrs_define
class DataProductEnvironment:
    """
    Attributes:
        environment_id (UUID):
        environment (EnvironmentGetItem):
        creation_date (datetime.datetime):
    """

    environment_id: UUID
    environment: EnvironmentGetItem
    creation_date: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        environment_id = str(self.environment_id)

        environment = self.environment.to_dict()

        creation_date = self.creation_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "environment_id": environment_id,
                "environment": environment,
                "creation_date": creation_date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.environment_get_item import EnvironmentGetItem  # noqa: PLC0415

        d = dict(src_dict)
        environment_id = UUID(d.pop("environment_id"))

        environment = EnvironmentGetItem.from_dict(d.pop("environment"))

        creation_date = datetime.datetime.fromisoformat(d.pop("creation_date"))

        data_product_environment = cls(
            environment_id=environment_id,
            environment=environment,
            creation_date=creation_date,
        )

        data_product_environment.additional_properties = d
        return data_product_environment

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
