from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.domain_status import DomainStatus


T = TypeVar("T", bound="GetDomainsItem")


@_attrs_define
class GetDomainsItem:
    """
    Attributes:
        id (UUID):
        name (str):
        namespace (str):
        description (str):
        status (DomainStatus):
        finalizers (list[str]):
        abstract_data_product_count (int):
    """

    id: UUID
    name: str
    namespace: str
    description: str
    status: DomainStatus
    finalizers: list[str]
    abstract_data_product_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)
        name = self.name
        namespace = self.namespace
        description = self.description
        status = self.status.value
        finalizers = self.finalizers

        abstract_data_product_count = self.abstract_data_product_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "namespace": namespace,
                "description": description,
                "status": status,
                "finalizers": finalizers,
                "abstract_data_product_count": abstract_data_product_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))
        name = d.pop("name")
        namespace = d.pop("namespace")
        description = d.pop("description")
        status = DomainStatus(d.pop("status"))
        finalizers = cast(list[str], d.pop("finalizers"))

        abstract_data_product_count = d.pop("abstract_data_product_count")

        get_domains_item = cls(
            id=id,
            name=name,
            namespace=namespace,
            description=description,
            status=status,
            finalizers=finalizers,
            abstract_data_product_count=abstract_data_product_count,
        )

        get_domains_item.additional_properties = d
        return get_domains_item

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
