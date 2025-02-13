from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NodeData")


@_attrs_define
class NodeData:
    """
    Attributes:
        id (Union[UUID, str]):
        name (str):
        link_to_id (Union[None, UUID, Unset, str]):
        icon_key (Union[None, Unset, str]):
    """

    id: Union[UUID, str]
    name: str
    link_to_id: Union[None, UUID, Unset, str] = UNSET
    icon_key: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id: str
        if isinstance(self.id, UUID):
            id = str(self.id)
        else:
            id = self.id

        name = self.name

        link_to_id: Union[None, Unset, str]
        if isinstance(self.link_to_id, Unset):
            link_to_id = UNSET
        elif isinstance(self.link_to_id, UUID):
            link_to_id = str(self.link_to_id)
        else:
            link_to_id = self.link_to_id

        icon_key: Union[None, Unset, str]
        if isinstance(self.icon_key, Unset):
            icon_key = UNSET
        else:
            icon_key = self.icon_key

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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_id(data: object) -> Union[UUID, str]:
            try:
                if not isinstance(data, str):
                    raise TypeError()
                id_type_1 = UUID(data)

                return id_type_1
            except:  # noqa: E722
                pass
            return cast(Union[UUID, str], data)

        id = _parse_id(d.pop("id"))

        name = d.pop("name")

        def _parse_link_to_id(data: object) -> Union[None, UUID, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                link_to_id_type_1 = UUID(data)

                return link_to_id_type_1
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset, str], data)

        link_to_id = _parse_link_to_id(d.pop("link_to_id", UNSET))

        def _parse_icon_key(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        icon_key = _parse_icon_key(d.pop("icon_key", UNSET))

        node_data = cls(
            id=id,
            name=name,
            link_to_id=link_to_id,
            icon_key=icon_key,
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
