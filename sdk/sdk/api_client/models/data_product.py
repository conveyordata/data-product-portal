from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_product_status import DataProductStatus

if TYPE_CHECKING:
    from ..models.data_product_type import DataProductType


T = TypeVar("T", bound="DataProduct")


@_attrs_define
class DataProduct:
    """
    Attributes:
        id (UUID):
        name (str):
        namespace (str):
        description (str):
        status (DataProductStatus):
        type_ (DataProductType):
    """

    id: UUID
    name: str
    namespace: str
    description: str
    status: DataProductStatus
    type_: DataProductType
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        namespace = self.namespace

        description = self.description

        status = self.status.value

        type_ = self.type_.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "namespace": namespace,
                "description": description,
                "status": status,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_product_type import DataProductType

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        namespace = d.pop("namespace")

        description = d.pop("description")

        status = DataProductStatus(d.pop("status"))

        type_ = DataProductType.from_dict(d.pop("type"))

        data_product = cls(
            id=id,
            name=name,
            namespace=namespace,
            description=description,
            status=status,
            type_=type_,
        )

        data_product.additional_properties = d
        return data_product

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
