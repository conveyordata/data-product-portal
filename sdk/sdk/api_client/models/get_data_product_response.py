from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_product_status import DataProductStatus

if TYPE_CHECKING:
    from ..models.data_product_life_cycle import DataProductLifeCycle
    from ..models.data_product_type import DataProductType
    from ..models.domain import Domain
    from ..models.tag import Tag


T = TypeVar("T", bound="GetDataProductResponse")


@_attrs_define
class GetDataProductResponse:
    """
    Attributes:
        id (UUID):
        name (str):
        description (str):
        namespace (str):
        status (DataProductStatus):
        tags (list[Tag]):
        usage (None | str):
        domain (Domain):
        type_ (DataProductType):
        lifecycle (DataProductLifeCycle | None):
        about (None | str):
    """

    id: UUID
    name: str
    description: str
    namespace: str
    status: DataProductStatus
    tags: list[Tag]
    usage: None | str
    domain: Domain
    type_: DataProductType
    lifecycle: DataProductLifeCycle | None
    about: None | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.data_product_life_cycle import DataProductLifeCycle

        id = str(self.id)

        name = self.name

        description = self.description

        namespace = self.namespace

        status = self.status.value

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        usage: None | str
        usage = self.usage

        domain = self.domain.to_dict()

        type_ = self.type_.to_dict()

        lifecycle: dict[str, Any] | None
        if isinstance(self.lifecycle, DataProductLifeCycle):
            lifecycle = self.lifecycle.to_dict()
        else:
            lifecycle = self.lifecycle

        about: None | str
        about = self.about

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "namespace": namespace,
                "status": status,
                "tags": tags,
                "usage": usage,
                "domain": domain,
                "type": type_,
                "lifecycle": lifecycle,
                "about": about,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_product_life_cycle import DataProductLifeCycle
        from ..models.data_product_type import DataProductType
        from ..models.domain import Domain
        from ..models.tag import Tag

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        description = d.pop("description")

        namespace = d.pop("namespace")

        status = DataProductStatus(d.pop("status"))

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        def _parse_usage(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        usage = _parse_usage(d.pop("usage"))

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

        def _parse_about(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        about = _parse_about(d.pop("about"))

        get_data_product_response = cls(
            id=id,
            name=name,
            description=description,
            namespace=namespace,
            status=status,
            tags=tags,
            usage=usage,
            domain=domain,
            type_=type_,
            lifecycle=lifecycle,
            about=about,
        )

        get_data_product_response.additional_properties = d
        return get_data_product_response

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
