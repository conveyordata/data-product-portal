from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.abstract_data_product_type import AbstractDataProductType

if TYPE_CHECKING:
    from ..models.domain import Domain


T = TypeVar("T", bound="GetAbstractDataProductResponse")


@_attrs_define
class GetAbstractDataProductResponse:
    """
    Attributes:
        id (UUID):
        name (str):
        namespace (str):
        description (str):
        domain (Domain):
        abstract_data_product_type (AbstractDataProductType):
    """

    id: UUID
    name: str
    namespace: str
    description: str
    domain: Domain
    abstract_data_product_type: AbstractDataProductType
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        namespace = self.namespace

        description = self.description

        domain = self.domain.to_dict()

        abstract_data_product_type = self.abstract_data_product_type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "namespace": namespace,
                "description": description,
                "domain": domain,
                "abstract_data_product_type": abstract_data_product_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.domain import Domain

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        namespace = d.pop("namespace")

        description = d.pop("description")

        domain = Domain.from_dict(d.pop("domain"))

        abstract_data_product_type = AbstractDataProductType(
            d.pop("abstract_data_product_type")
        )

        get_abstract_data_product_response = cls(
            id=id,
            name=name,
            namespace=namespace,
            description=description,
            domain=domain,
            abstract_data_product_type=abstract_data_product_type,
        )

        get_abstract_data_product_response.additional_properties = d
        return get_abstract_data_product_response

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
