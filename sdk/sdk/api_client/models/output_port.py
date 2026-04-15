from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.output_port_access_type import OutputPortAccessType
from ..models.output_port_status import OutputPortStatus

if TYPE_CHECKING:
    from ..models.tag import Tag


T = TypeVar("T", bound="OutputPort")


@_attrs_define
class OutputPort:
    """
    Attributes:
        id (UUID):
        name (str):
        namespace (str):
        description (str):
        status (OutputPortStatus):
        access_type (OutputPortAccessType):
        data_product_id (UUID):
        tags (list[Tag]):
    """

    id: UUID
    name: str
    namespace: str
    description: str
    status: OutputPortStatus
    access_type: OutputPortAccessType
    data_product_id: UUID
    tags: list[Tag]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        namespace = self.namespace

        description = self.description

        status = self.status.value

        access_type = self.access_type.value

        data_product_id = str(self.data_product_id)

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "namespace": namespace,
                "description": description,
                "status": status,
                "access_type": access_type,
                "data_product_id": data_product_id,
                "tags": tags,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tag import Tag

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        namespace = d.pop("namespace")

        description = d.pop("description")

        status = OutputPortStatus(d.pop("status"))

        access_type = OutputPortAccessType(d.pop("access_type"))

        data_product_id = UUID(d.pop("data_product_id"))

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        output_port = cls(
            id=id,
            name=name,
            namespace=namespace,
            description=description,
            status=status,
            access_type=access_type,
            data_product_id=data_product_id,
            tags=tags,
        )

        output_port.additional_properties = d
        return output_port

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
