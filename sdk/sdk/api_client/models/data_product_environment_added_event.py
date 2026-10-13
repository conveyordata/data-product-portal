from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DataProductEnvironmentAddedEvent")


@_attrs_define
class DataProductEnvironmentAddedEvent:
    """
    Attributes:
        data_product_id (UUID):
        environment (str):
        creation_date (datetime.datetime):
    """

    data_product_id: UUID
    environment: str
    creation_date: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data_product_id = str(self.data_product_id)

        environment = self.environment

        creation_date = self.creation_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_product_id": data_product_id,
                "environment": environment,
                "creation_date": creation_date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        data_product_id = UUID(d.pop("data_product_id"))

        environment = d.pop("environment")

        creation_date = datetime.datetime.fromisoformat(d.pop("creation_date"))

        data_product_environment_added_event = cls(
            data_product_id=data_product_id,
            environment=environment,
            creation_date=creation_date,
        )

        data_product_environment_added_event.additional_properties = d
        return data_product_environment_added_event

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
