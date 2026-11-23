from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.data_product_life_cycle import DataProductLifeCycle
    from ..models.data_product_type import DataProductType
    from ..models.domain import Domain
    from ..models.search_data_products_output_port import SearchDataProductsOutputPort
    from ..models.tag import Tag


T = TypeVar("T", bound="SearchDataProductsResponseItem")


@_attrs_define
class SearchDataProductsResponseItem:
    """
    Attributes:
        id (UUID):
        name (str):
        description (str):
        tags (list[Tag]):
        domain (Domain):
        type_ (DataProductType):
        lifecycle (DataProductLifeCycle | None):
        output_ports (list[SearchDataProductsOutputPort]):
        consumer_count (int):
    """

    id: UUID
    name: str
    description: str
    tags: list[Tag]
    domain: Domain
    type_: DataProductType
    lifecycle: DataProductLifeCycle | None
    output_ports: list[SearchDataProductsOutputPort]
    consumer_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.data_product_life_cycle import (
            DataProductLifeCycle,  # noqa: PLC0415
        )

        id = str(self.id)

        name = self.name

        description = self.description

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        domain = self.domain.to_dict()

        type_ = self.type_.to_dict()

        lifecycle: dict[str, Any] | None
        if isinstance(self.lifecycle, DataProductLifeCycle):
            lifecycle = self.lifecycle.to_dict()
        else:
            lifecycle = self.lifecycle

        output_ports = []
        for output_ports_item_data in self.output_ports:
            output_ports_item = output_ports_item_data.to_dict()
            output_ports.append(output_ports_item)

        consumer_count = self.consumer_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "tags": tags,
                "domain": domain,
                "type": type_,
                "lifecycle": lifecycle,
                "output_ports": output_ports,
                "consumer_count": consumer_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_product_life_cycle import (
            DataProductLifeCycle,  # noqa: PLC0415
        )
        from ..models.data_product_type import DataProductType  # noqa: PLC0415
        from ..models.domain import Domain  # noqa: PLC0415
        from ..models.search_data_products_output_port import (
            SearchDataProductsOutputPort,  # noqa: PLC0415
        )
        from ..models.tag import Tag  # noqa: PLC0415

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        description = d.pop("description")

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        domain = Domain.from_dict(d.pop("domain"))

        type_ = DataProductType.from_dict(d.pop("type"))

        def _parse_lifecycle(data: object) -> DataProductLifeCycle | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                lifecycle_type_0 = DataProductLifeCycle.from_dict(data)

                return lifecycle_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DataProductLifeCycle | None, data)

        lifecycle = _parse_lifecycle(d.pop("lifecycle"))

        output_ports = []
        _output_ports = d.pop("output_ports")
        for output_ports_item_data in _output_ports:
            output_ports_item = SearchDataProductsOutputPort.from_dict(
                output_ports_item_data
            )

            output_ports.append(output_ports_item)

        consumer_count = d.pop("consumer_count")

        search_data_products_response_item = cls(
            id=id,
            name=name,
            description=description,
            tags=tags,
            domain=domain,
            type_=type_,
            lifecycle=lifecycle,
            output_ports=output_ports,
            consumer_count=consumer_count,
        )

        search_data_products_response_item.additional_properties = d
        return search_data_products_response_item

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
