from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.request_input_ports_for_data_product_request import (
        RequestInputPortsForDataProductRequest,
    )


T = TypeVar("T", bound="DataProductCreate")


@_attrs_define
class DataProductCreate:
    """
    Attributes:
        name (str):
        namespace (str):
        description (str):
        type_id (UUID):
        domain_id (UUID):
        lifecycle_id (UUID):
        owners (list[UUID]):
        about (None | str | Unset):
        tag_ids (list[UUID] | Unset):
        input_ports (None | RequestInputPortsForDataProductRequest | Unset):
    """

    name: str
    namespace: str
    description: str
    type_id: UUID
    domain_id: UUID
    lifecycle_id: UUID
    owners: list[UUID]
    about: None | str | Unset = UNSET
    tag_ids: list[UUID] | Unset = UNSET
    input_ports: None | RequestInputPortsForDataProductRequest | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.request_input_ports_for_data_product_request import (
            RequestInputPortsForDataProductRequest,
        )

        name = self.name

        namespace = self.namespace

        description = self.description

        type_id = str(self.type_id)

        domain_id = str(self.domain_id)

        lifecycle_id = str(self.lifecycle_id)

        owners = []
        for owners_item_data in self.owners:
            owners_item = str(owners_item_data)
            owners.append(owners_item)

        about: None | str | Unset
        if isinstance(self.about, Unset):
            about = UNSET
        else:
            about = self.about

        tag_ids: list[str] | Unset = UNSET
        if not isinstance(self.tag_ids, Unset):
            tag_ids = []
            for tag_ids_item_data in self.tag_ids:
                tag_ids_item = str(tag_ids_item_data)
                tag_ids.append(tag_ids_item)

        input_ports: dict[str, Any] | None | Unset
        if isinstance(self.input_ports, Unset):
            input_ports = UNSET
        elif isinstance(self.input_ports, RequestInputPortsForDataProductRequest):
            input_ports = self.input_ports.to_dict()
        else:
            input_ports = self.input_ports

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "namespace": namespace,
                "description": description,
                "type_id": type_id,
                "domain_id": domain_id,
                "lifecycle_id": lifecycle_id,
                "owners": owners,
            }
        )
        if about is not UNSET:
            field_dict["about"] = about
        if tag_ids is not UNSET:
            field_dict["tag_ids"] = tag_ids
        if input_ports is not UNSET:
            field_dict["input_ports"] = input_ports

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.request_input_ports_for_data_product_request import (
            RequestInputPortsForDataProductRequest,
        )

        d = dict(src_dict)
        name = d.pop("name")

        namespace = d.pop("namespace")

        description = d.pop("description")

        type_id = UUID(d.pop("type_id"))

        domain_id = UUID(d.pop("domain_id"))

        lifecycle_id = UUID(d.pop("lifecycle_id"))

        owners = []
        _owners = d.pop("owners")
        for owners_item_data in _owners:
            owners_item = UUID(owners_item_data)

            owners.append(owners_item)

        def _parse_about(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        about = _parse_about(d.pop("about", UNSET))

        _tag_ids = d.pop("tag_ids", UNSET)
        tag_ids: list[UUID] | Unset = UNSET
        if _tag_ids is not UNSET:
            tag_ids = []
            for tag_ids_item_data in _tag_ids:
                tag_ids_item = UUID(tag_ids_item_data)

                tag_ids.append(tag_ids_item)

        def _parse_input_ports(
            data: object,
        ) -> None | RequestInputPortsForDataProductRequest | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                input_ports_type_0 = RequestInputPortsForDataProductRequest.from_dict(
                    data
                )

                return input_ports_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RequestInputPortsForDataProductRequest | Unset, data)

        input_ports = _parse_input_ports(d.pop("input_ports", UNSET))

        data_product_create = cls(
            name=name,
            namespace=namespace,
            description=description,
            type_id=type_id,
            domain_id=domain_id,
            lifecycle_id=lifecycle_id,
            owners=owners,
            about=about,
            tag_ids=tag_ids,
            input_ports=input_ports,
        )

        data_product_create.additional_properties = d
        return data_product_create

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
