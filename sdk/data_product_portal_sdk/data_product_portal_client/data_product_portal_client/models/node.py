from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.node_type import NodeType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_data import NodeData


T = TypeVar("T", bound="Node")


@_attrs_define
class Node:
    """
    Attributes:
        id (Union[UUID, str]):
        data (NodeData):
        type_ (NodeType):
        is_main (Union[Unset, bool]):  Default: False.
    """

    id: Union[UUID, str]
    data: "NodeData"
    type_: NodeType
    is_main: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id: str
        if isinstance(self.id, UUID):
            id = str(self.id)
        else:
            id = self.id

        data = self.data.to_dict()

        type_ = self.type_.value

        is_main = self.is_main

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "data": data,
                "type": type_,
            }
        )
        if is_main is not UNSET:
            field_dict["isMain"] = is_main

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.node_data import NodeData

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

        data = NodeData.from_dict(d.pop("data"))

        type_ = NodeType(d.pop("type"))

        is_main = d.pop("isMain", UNSET)

        node = cls(
            id=id,
            data=data,
            type_=type_,
            is_main=is_main,
        )

        node.additional_properties = d
        return node

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
