from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Edge")


@_attrs_define
class Edge:
    """
    Attributes:
        id (Union[UUID, str]):
        source (Union[UUID, str]):
        target (Union[UUID, str]):
        animated (bool):
        source_handle (Union[Unset, str]):  Default: 'right_s'.
        target_handle (Union[Unset, str]):  Default: 'left_t'.
    """

    id: Union[UUID, str]
    source: Union[UUID, str]
    target: Union[UUID, str]
    animated: bool
    source_handle: Union[Unset, str] = "right_s"
    target_handle: Union[Unset, str] = "left_t"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id: str
        if isinstance(self.id, UUID):
            id = str(self.id)
        else:
            id = self.id

        source: str
        if isinstance(self.source, UUID):
            source = str(self.source)
        else:
            source = self.source

        target: str
        if isinstance(self.target, UUID):
            target = str(self.target)
        else:
            target = self.target

        animated = self.animated

        source_handle = self.source_handle

        target_handle = self.target_handle

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "source": source,
                "target": target,
                "animated": animated,
            }
        )
        if source_handle is not UNSET:
            field_dict["sourceHandle"] = source_handle
        if target_handle is not UNSET:
            field_dict["targetHandle"] = target_handle

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

        def _parse_source(data: object) -> Union[UUID, str]:
            try:
                if not isinstance(data, str):
                    raise TypeError()
                source_type_1 = UUID(data)

                return source_type_1
            except:  # noqa: E722
                pass
            return cast(Union[UUID, str], data)

        source = _parse_source(d.pop("source"))

        def _parse_target(data: object) -> Union[UUID, str]:
            try:
                if not isinstance(data, str):
                    raise TypeError()
                target_type_1 = UUID(data)

                return target_type_1
            except:  # noqa: E722
                pass
            return cast(Union[UUID, str], data)

        target = _parse_target(d.pop("target"))

        animated = d.pop("animated")

        source_handle = d.pop("sourceHandle", UNSET)

        target_handle = d.pop("targetHandle", UNSET)

        edge = cls(
            id=id,
            source=source,
            target=target,
            animated=animated,
            source_handle=source_handle,
            target_handle=target_handle,
        )

        edge.additional_properties = d
        return edge

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
