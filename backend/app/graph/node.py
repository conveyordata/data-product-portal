from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class NodeData(BaseModel):
    id: str | UUID
    name: str
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
