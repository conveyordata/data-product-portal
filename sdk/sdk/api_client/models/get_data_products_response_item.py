from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.abstract_data_product_status import AbstractDataProductStatus
from ..models.data_product_visibility import DataProductVisibility

if TYPE_CHECKING:
    from ..models.data_product_type import DataProductType
    from ..models.domain import Domain
    from ..models.tag import Tag


T = TypeVar("T", bound="GetDataProductsResponseItem")


@_attrs_define
class GetDataProductsResponseItem:
    """
    Attributes:
        id (UUID):
        name (str):
        description (str):
        namespace (str):
        status (AbstractDataProductStatus):
        finalizers (list[str]):
        tags (list[Tag]):
        usage (None | str):
        domain (Domain):
        type_ (DataProductType):
        visibility (DataProductVisibility):
        user_count (int):
        input_port_count (int):
        technical_asset_count (int):
    """

    id: UUID
    name: str
    description: str
    namespace: str
    status: AbstractDataProductStatus
    finalizers: list[str]
    tags: list[Tag]
    usage: None | str
    domain: Domain
    type_: DataProductType
    visibility: DataProductVisibility
    user_count: int
    input_port_count: int
    technical_asset_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        description = self.description

        namespace = self.namespace

        status = self.status.value

        finalizers = self.finalizers

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        usage: None | str
        usage = self.usage

        domain = self.domain.to_dict()

        type_ = self.type_.to_dict()

        visibility = self.visibility.value

        user_count = self.user_count

        input_port_count = self.input_port_count

        technical_asset_count = self.technical_asset_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "namespace": namespace,
                "status": status,
                "finalizers": finalizers,
                "tags": tags,
                "usage": usage,
                "domain": domain,
                "type": type_,
                "visibility": visibility,
                "user_count": user_count,
                "input_port_count": input_port_count,
                "technical_asset_count": technical_asset_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_product_type import DataProductType
        from ..models.domain import Domain
        from ..models.tag import Tag

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        description = d.pop("description")

        namespace = d.pop("namespace")

        status = AbstractDataProductStatus(d.pop("status"))

        finalizers = cast(list[str], d.pop("finalizers"))

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

        visibility = DataProductVisibility(d.pop("visibility"))

        user_count = d.pop("user_count")

        input_port_count = d.pop("input_port_count")

        technical_asset_count = d.pop("technical_asset_count")

        get_data_products_response_item = cls(
            id=id,
            name=name,
            description=description,
            namespace=namespace,
            status=status,
            finalizers=finalizers,
            tags=tags,
            usage=usage,
            domain=domain,
            type_=type_,
            visibility=visibility,
            user_count=user_count,
            input_port_count=input_port_count,
            technical_asset_count=technical_asset_count,
        )

        get_data_products_response_item.additional_properties = d
        return get_data_products_response_item

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
