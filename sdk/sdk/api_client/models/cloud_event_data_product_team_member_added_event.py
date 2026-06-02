from __future__ import annotations

from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.data_product_team_member_added_event import (
        DataProductTeamMemberAddedEvent,
    )


T = TypeVar("T", bound="CloudEventDataProductTeamMemberAddedEvent")


@_attrs_define
class CloudEventDataProductTeamMemberAddedEvent:
    """
    Attributes:
        id (str): A unique UUID identifier for this specific event instance.
        time (str): Timestamp of when the event occurred in ISO 8601 UTC format.
        data (DataProductTeamMemberAddedEvent):
        specversion (str | Unset): The CloudEvents specification version. Default: '1.0'.
        source (str | Unset): Identifies the context in which an event happened. Default: 'data-product-portal'.
        type_ (Literal['data_product.team_member_added'] | Unset): The unique type string belonging to this event.
            Default: 'data_product.team_member_added'.
    """

    id: str
    time: str
    data: DataProductTeamMemberAddedEvent
    specversion: str | Unset = "1.0"
    source: str | Unset = "data-product-portal"
    type_: Literal["data_product.team_member_added"] | Unset = (
        "data_product.team_member_added"
    )
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        time = self.time

        data = self.data.to_dict()

        specversion = self.specversion

        source = self.source

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "time": time,
                "data": data,
            }
        )
        if specversion is not UNSET:
            field_dict["specversion"] = specversion
        if source is not UNSET:
            field_dict["source"] = source
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_product_team_member_added_event import (
            DataProductTeamMemberAddedEvent,
        )

        d = dict(src_dict)
        id = d.pop("id")

        time = d.pop("time")

        data = DataProductTeamMemberAddedEvent.from_dict(d.pop("data"))

        specversion = d.pop("specversion", UNSET)

        source = d.pop("source", UNSET)

        type_ = cast(
            Literal["data_product.team_member_added"] | Unset, d.pop("type", UNSET)
        )
        if type_ != "data_product.team_member_added" and not isinstance(type_, Unset):
            raise ValueError(
                f"type must match const 'data_product.team_member_added', got '{type_}'"
            )

        cloud_event_data_product_team_member_added_event = cls(
            id=id,
            time=time,
            data=data,
            specversion=specversion,
            source=source,
            type_=type_,
        )

        cloud_event_data_product_team_member_added_event.additional_properties = d
        return cloud_event_data_product_team_member_added_event

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
