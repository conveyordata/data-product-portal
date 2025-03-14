from typing import Iterable

from pydantic import BaseModel, Field

from app.graph.edge import Edge
from app.graph.node import Node


class Graph(BaseModel):
    edges: Iterable[Edge] = Field(..., description="Collection of edges in the graph")
    nodes: Iterable[Node] = Field(..., description="Collection of nodes in the graph")
