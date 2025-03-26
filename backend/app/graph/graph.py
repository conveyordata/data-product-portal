from pydantic import BaseModel

from app.graph.edge import Edge
from app.graph.node import Node


class Graph(BaseModel):
    edges: set[Edge]
    nodes: set[Node]
