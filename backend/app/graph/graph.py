from pydantic import BaseModel

from app.graph.edge import Edge
from app.graph.node import Node


class Graph(BaseModel):
    edges: list[Edge]
    nodes: list[Node]
