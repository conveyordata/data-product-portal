from enum import IntEnum, StrEnum
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.core.authz.actions import AuthorizationAction
from app.shared.schema import ORMModel


class Scope(StrEnum):
    DATASET = "dataset"
    DATA_PRODUCT = "data_product"
    DOMAIN = "domain"
    GLOBAL = "global"


class Prototype(IntEnum):
    CUSTOM = 0
    EVERYONE = 1
    OWNER = 2


class CreateRole(ORMModel):
    name: str = Field(..., description="Name of the role")
    scope: Scope = Field(..., description="Scope of the role")
    description: str = Field(..., description="Description of the role")
    permissions: list[AuthorizationAction] = Field(
        ..., description="List of permissions associated with the role"
    )


class UpdateRole(ORMModel):
    id: UUID = Field(..., description="Unique identifier for the role")
    name: Optional[str] = Field(None, description="Name of the role")
    description: Optional[str] = Field(None, description="Description of the role")
    permissions: Optional[list[AuthorizationAction]] = Field(
        None, description="List of permissions associated with the role"
    )


class Role(CreateRole):
    id: UUID = Field(..., description="Unique identifier for the role")
    prototype: Prototype = Field(..., description="Prototype type of the role")
