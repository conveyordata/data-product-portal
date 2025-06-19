from typing import Optional
from uuid import UUID

from pydantic import EmailStr, NaiveDatetime

from app.role_assignments.data_product.schema import (
    RoleAssignmentResponse as DataProductRoleAssignmentResponse,
)
from app.role_assignments.dataset.schema import (
    RoleAssignmentResponse as DatasetRoleAssignmentResponse,
)
from app.role_assignments.global_.schema import RoleAssignmentResponse
from app.shared.schema import ORMModel


class BaseUserGet(ORMModel):
    id: UUID
    email: EmailStr
    external_id: str
    first_name: str
    last_name: str


class UserGet(BaseUserGet):
    phone: Optional[str]
    bio: Optional[str]
    profile_picture: Optional[str]
    location: Optional[str]
    last_login: Optional[NaiveDatetime]
    created_on: NaiveDatetime
    dataset_roles: list[DatasetRoleAssignmentResponse]
    data_product_roles: list[DataProductRoleAssignmentResponse]


class UsersGet(BaseUserGet):
    global_role: Optional[RoleAssignmentResponse]
