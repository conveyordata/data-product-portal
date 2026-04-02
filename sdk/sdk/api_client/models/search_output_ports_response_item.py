from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_quality_status import DataQualityStatus
from ..models.output_port_access_type import OutputPortAccessType
from ..models.output_port_status import OutputPortStatus

if TYPE_CHECKING:
    from ..models.data_product_life_cycle import DataProductLifeCycle
    from ..models.domain import Domain
    from ..models.tag import Tag


T = TypeVar("T", bound="SearchOutputPortsResponseItem")


@_attrs_define
class SearchOutputPortsResponseItem:
    """
    Attributes:
        id (UUID):
        namespace (str):
        name (str):
        description (str):
        status (OutputPortStatus):
        usage (None | str):
        access_type (OutputPortAccessType):
        data_product_id (UUID):
        tags (list[Tag]):
        domain (Domain):
        lifecycle (DataProductLifeCycle | None):
        data_product_count (int):
        technical_assets_count (int):
        data_product_name (str):
        quality_status (DataQualityStatus | None):
    """

    id: UUID
    namespace: str
    name: str
    description: str
    status: OutputPortStatus
    usage: None | str
    access_type: OutputPortAccessType
    data_product_id: UUID
    tags: list[Tag]
    domain: Domain
    lifecycle: DataProductLifeCycle | None
    data_product_count: int
    technical_assets_count: int
    data_product_name: str
    quality_status: DataQualityStatus | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.data_product_life_cycle import DataProductLifeCycle

        id = str(self.id)

        namespace = self.namespace

        name = self.name

        description = self.description

        status = self.status.value

        usage: None | str
        usage = self.usage

        access_type = self.access_type.value

        data_product_id = str(self.data_product_id)

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        domain = self.domain.to_dict()

        lifecycle: dict[str, Any] | None
        if isinstance(self.lifecycle, DataProductLifeCycle):
            lifecycle = self.lifecycle.to_dict()
        else:
            lifecycle = self.lifecycle

        data_product_count = self.data_product_count

        technical_assets_count = self.technical_assets_count

        data_product_name = self.data_product_name

        quality_status: None | str
        if isinstance(self.quality_status, DataQualityStatus):
            quality_status = self.quality_status.value
        else:
            quality_status = self.quality_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "namespace": namespace,
                "name": name,
                "description": description,
                "status": status,
                "usage": usage,
                "access_type": access_type,
                "data_product_id": data_product_id,
                "tags": tags,
                "domain": domain,
                "lifecycle": lifecycle,
                "data_product_count": data_product_count,
                "technical_assets_count": technical_assets_count,
                "data_product_name": data_product_name,
                "quality_status": quality_status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_product_life_cycle import DataProductLifeCycle
        from ..models.domain import Domain
        from ..models.tag import Tag

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        namespace = d.pop("namespace")

        name = d.pop("name")

        description = d.pop("description")

        status = OutputPortStatus(d.pop("status"))

        def _parse_usage(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        usage = _parse_usage(d.pop("usage"))

        access_type = OutputPortAccessType(d.pop("access_type"))

        data_product_id = UUID(d.pop("data_product_id"))

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        domain = Domain.from_dict(d.pop("domain"))

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

        data_product_count = d.pop("data_product_count")

        technical_assets_count = d.pop("technical_assets_count")

        data_product_name = d.pop("data_product_name")

        def _parse_quality_status(data: object) -> DataQualityStatus | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                quality_status_type_0 = DataQualityStatus(data)

                return quality_status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DataQualityStatus | None, data)

        quality_status = _parse_quality_status(d.pop("quality_status"))

        search_output_ports_response_item = cls(
            id=id,
            namespace=namespace,
            name=name,
            description=description,
            status=status,
            usage=usage,
            access_type=access_type,
            data_product_id=data_product_id,
            tags=tags,
            domain=domain,
            lifecycle=lifecycle,
            data_product_count=data_product_count,
            technical_assets_count=technical_assets_count,
            data_product_name=data_product_name,
            quality_status=quality_status,
        )

        search_output_ports_response_item.additional_properties = d
        return search_output_ports_response_item

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
