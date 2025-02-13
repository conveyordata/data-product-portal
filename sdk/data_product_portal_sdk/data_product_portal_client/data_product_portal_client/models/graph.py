from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.edge import Edge
    from ..models.node import Node


T = TypeVar("T", bound="Graph")


@_attrs_define
class Graph:
    """
    Attributes:
        edges (list['Edge']):
        nodes (list['Node']):
    """

    edges: list["Edge"]
    nodes: list["Node"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        edges = []
        for edges_item_data in self.edges:
            edges_item = edges_item_data.to_dict()
            edges.append(edges_item)

        nodes = []
        for nodes_item_data in self.nodes:
            nodes_item = nodes_item_data.to_dict()
            nodes.append(nodes_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "edges": edges,
                "nodes": nodes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.edge import Edge
        from ..models.node import Node

        d = src_dict.copy()
        edges = []
        _edges = d.pop("edges")
        for edges_item_data in _edges:
            edges_item = Edge.from_dict(edges_item_data)

            edges.append(edges_item)

        nodes = []
        _nodes = d.pop("nodes")
        for nodes_item_data in _nodes:
            nodes_item = Node.from_dict(nodes_item_data)

            nodes.append(nodes_item)

        graph = cls(
            edges=edges,
            nodes=nodes,
        )

        graph.additional_properties = d
        return graph

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
