from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.output_port_access_type import OutputPortAccessType
from ..types import UNSET, Unset

T = TypeVar("T", bound="DatasetUpdate")


@_attrs_define
class DatasetUpdate:
    """
    Attributes:
        name (str):
        namespace (str):
        description (str):
        access_type (OutputPortAccessType):
        tag_ids (list[UUID]):
        about (None | str | Unset):
        lifecycle_id (None | Unset | UUID):
    """

    name: str
    namespace: str
    description: str
    access_type: OutputPortAccessType
    tag_ids: list[UUID]
    about: None | str | Unset = UNSET
    lifecycle_id: None | Unset | UUID = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        namespace = self.namespace

        description = self.description

        access_type = self.access_type.value

        tag_ids = []
        for tag_ids_item_data in self.tag_ids:
            tag_ids_item = str(tag_ids_item_data)
            tag_ids.append(tag_ids_item)

        about: None | str | Unset
        if isinstance(self.about, Unset):
            about = UNSET
        else:
            about = self.about

        lifecycle_id: None | str | Unset
        if isinstance(self.lifecycle_id, Unset):
            lifecycle_id = UNSET
        elif isinstance(self.lifecycle_id, UUID):
            lifecycle_id = str(self.lifecycle_id)
        else:
            lifecycle_id = self.lifecycle_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "namespace": namespace,
                "description": description,
                "access_type": access_type,
                "tag_ids": tag_ids,
            }
        )
        if about is not UNSET:
            field_dict["about"] = about
        if lifecycle_id is not UNSET:
            field_dict["lifecycle_id"] = lifecycle_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        namespace = d.pop("namespace")

        description = d.pop("description")

        access_type = OutputPortAccessType(d.pop("access_type"))

        tag_ids = []
        _tag_ids = d.pop("tag_ids")
        for tag_ids_item_data in _tag_ids:
            tag_ids_item = UUID(tag_ids_item_data)

            tag_ids.append(tag_ids_item)

        def _parse_about(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        about = _parse_about(d.pop("about", UNSET))

        def _parse_lifecycle_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                lifecycle_id_type_0 = UUID(data)

                return lifecycle_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        lifecycle_id = _parse_lifecycle_id(d.pop("lifecycle_id", UNSET))

        dataset_update = cls(
            name=name,
            namespace=namespace,
            description=description,
            access_type=access_type,
            tag_ids=tag_ids,
            about=about,
            lifecycle_id=lifecycle_id,
        )

        dataset_update.additional_properties = d
        return dataset_update

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
