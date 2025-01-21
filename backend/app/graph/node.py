from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class NodeData(BaseModel):
    id: str | UUID
    name: str
    link_to_id: Optional[str | UUID] = None
    icon_key: Optional[str] = None


class NodeType(str, Enum):
    dataProductNode = "dataProductNode"
    dataOutputNode = "dataOutputNode"
    datasetNode = "datasetNode"


class Node(BaseModel):
    id: str | UUID
    data: NodeData
    type: NodeType
    isMain: bool = False

    def __hash__(self) -> int:
        return self.id.__hash__()
