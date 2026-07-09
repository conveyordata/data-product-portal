from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.output_port_access_duration import OutputPortAccessDuration


T = TypeVar("T", bound="GetOutputPortAccessDurationsResponse")


@_attrs_define
class GetOutputPortAccessDurationsResponse:
    """
    Attributes:
        id (UUID):
        data_product_access_duration (OutputPortAccessDuration):
        exploration_access_duration (OutputPortAccessDuration):
    """

    id: UUID
    data_product_access_duration: OutputPortAccessDuration
    exploration_access_duration: OutputPortAccessDuration
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        data_product_access_duration = self.data_product_access_duration.to_dict()

        exploration_access_duration = self.exploration_access_duration.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "data_product_access_duration": data_product_access_duration,
                "exploration_access_duration": exploration_access_duration,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.output_port_access_duration import OutputPortAccessDuration

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        data_product_access_duration = OutputPortAccessDuration.from_dict(
            d.pop("data_product_access_duration")
        )

        exploration_access_duration = OutputPortAccessDuration.from_dict(
            d.pop("exploration_access_duration")
        )

        get_output_port_access_durations_response = cls(
            id=id,
            data_product_access_duration=data_product_access_duration,
            exploration_access_duration=exploration_access_duration,
        )

        get_output_port_access_durations_response.additional_properties = d
        return get_output_port_access_durations_response

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
