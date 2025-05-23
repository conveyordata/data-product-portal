from enum import Enum
from typing import Optional, Sequence
from uuid import UUID

from pydantic import BaseModel

from app.role_assignments.data_product.schema import (
    RoleAssignment as DataProductRoleAssignment,
)
from app.role_assignments.dataset.schema import RoleAssignment as DatasetRoleAssignment


class NodeData(BaseModel):
    id: str | UUID
    name: str
    link_to_id: Optional[str | UUID] = None
    icon_key: Optional[str] = None
    domain: Optional[str] = None
    domain_id: Optional[str | UUID] = None
    description: Optional[str] = None
    assignments: Optional[
        Sequence[DataProductRoleAssignment | DatasetRoleAssignment]
    ] = None


class NodeType(str, Enum):
    dataProductNode = "dataProductNode"
    dataOutputNode = "dataOutputNode"
    datasetNode = "datasetNode"
    domainNode = "domainNode"


class Node(BaseModel):
    id: str | UUID
    data: NodeData
    type: NodeType
    isMain: bool = False

    def __hash__(self) -> int:
        return self.id.__hash__()
