from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NodeData")


@_attrs_define
class NodeData:
    """
    Attributes:
        id (str | UUID):
        name (str):
        link_to_id (None | str | Unset | UUID):
        icon_key (None | str | Unset):
        domain (None | str | Unset):
        domain_id (None | str | Unset | UUID):
        description (None | str | Unset):
    """

    id: str | UUID
    name: str
    link_to_id: None | str | Unset | UUID = UNSET
    icon_key: None | str | Unset = UNSET
    domain: None | str | Unset = UNSET
    domain_id: None | str | Unset | UUID = UNSET
    description: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id: str
        if isinstance(self.id, UUID):
            id = str(self.id)
        else:
            id = self.id

        name = self.name

        link_to_id: None | str | Unset
        if isinstance(self.link_to_id, Unset):
            link_to_id = UNSET
        elif isinstance(self.link_to_id, UUID):
            link_to_id = str(self.link_to_id)
        else:
            link_to_id = self.link_to_id

        icon_key: None | str | Unset
        if isinstance(self.icon_key, Unset):
            icon_key = UNSET
        else:
            icon_key = self.icon_key

        domain: None | str | Unset
        if isinstance(self.domain, Unset):
            domain = UNSET
        else:
            domain = self.domain

        domain_id: None | str | Unset
        if isinstance(self.domain_id, Unset):
            domain_id = UNSET
        elif isinstance(self.domain_id, UUID):
            domain_id = str(self.domain_id)
        else:
            domain_id = self.domain_id

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
            }
        )
        if link_to_id is not UNSET:
            field_dict["link_to_id"] = link_to_id
        if icon_key is not UNSET:
            field_dict["icon_key"] = icon_key
        if domain is not UNSET:
            field_dict["domain"] = domain
        if domain_id is not UNSET:
            field_dict["domain_id"] = domain_id
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_id(data: object) -> str | UUID:
            try:
                if not isinstance(data, str):
                    raise TypeError()
                id_type_1 = UUID(data)

                return id_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(str | UUID, data)

        id = _parse_id(d.pop("id"))

        name = d.pop("name")

        def _parse_link_to_id(data: object) -> None | str | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                link_to_id_type_1 = UUID(data)

                return link_to_id_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | str | Unset | UUID, data)

        link_to_id = _parse_link_to_id(d.pop("link_to_id", UNSET))

        def _parse_icon_key(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        icon_key = _parse_icon_key(d.pop("icon_key", UNSET))

        def _parse_domain(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        domain = _parse_domain(d.pop("domain", UNSET))

        def _parse_domain_id(data: object) -> None | str | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                domain_id_type_1 = UUID(data)

                return domain_id_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | str | Unset | UUID, data)

        domain_id = _parse_domain_id(d.pop("domain_id", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        node_data = cls(
            id=id,
            name=name,
            link_to_id=link_to_id,
            icon_key=icon_key,
            domain=domain,
            domain_id=domain_id,
            description=description,
        )

        node_data.additional_properties = d
        return node_data

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
