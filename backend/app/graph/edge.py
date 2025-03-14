from uuid import UUID

from pydantic import BaseModel, Field


class Edge(BaseModel):
    id: str | UUID = Field(..., description="Unique identifier for the edge")
    source: str | UUID = Field(..., description="Source node identifier for the edge")
    target: str | UUID = Field(..., description="Target node identifier for the edge")
    animated: bool = Field(..., description="Indicates if the edge is animated")
    sourceHandle: str = Field(
        "right_s", description="Handle position on the source node"
    )
    targetHandle: str = Field(
        "left_t", description="Handle position on the target node"
    )

    def __hash__(self) -> int:
        return self.id.__hash__()
