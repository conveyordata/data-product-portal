from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class NodeData(BaseModel):
    id: str | UUID = Field(..., description="Unique identifier for the node data")
    name: str = Field(..., description="Name of the node")
    link_to_id: Optional[str | UUID] = Field(
        None, description="Optional link to another node's identifier"
    )
    icon_key: Optional[str] = Field(None, description="Optional icon key for the node")


class NodeType(str, Enum):
    dataProductNode = "dataProductNode"
    dataOutputNode = "dataOutputNode"
    datasetNode = "datasetNode"


class Node(BaseModel):
    id: str | UUID = Field(..., description="Unique identifier for the node")
    data: NodeData = Field(..., description="Data associated with the node")
    type: NodeType = Field(..., description="Type of the node")
    isMain: bool = Field(False, description="Indicates if this is the main node")

    def __hash__(self) -> int:
        return self.id.__hash__()
