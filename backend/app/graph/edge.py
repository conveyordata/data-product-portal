from uuid import UUID

from pydantic import BaseModel


class Edge(BaseModel):
    id: str | UUID
    source: str | UUID
    target: str | UUID
    animated: bool
    sourceHandle: str = "right_s"
    targetHandle: str = "left_t"

    def __hash__(self) -> int:
        return self.id.__hash__()
