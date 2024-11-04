from uuid import UUID

from pydantic import BaseModel


class Edge(BaseModel):
    id: str | UUID
    source: str | UUID
    target: str | UUID
    animated: bool
