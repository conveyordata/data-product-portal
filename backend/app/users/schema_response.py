from datetime import datetime
from typing import Literal, Optional, Sequence, Union
from uuid import UUID

from pydantic import EmailStr

from app.authorization.role_assignments.data_product.schema import (
    DataProductRoleAssignmentResponse,
)
from app.authorization.role_assignments.global_.schema import (
    GlobalRoleAssignmentResponse,
)
from app.data_products.output_port_technical_assets_link.schema_response import (
    TechnicalAssetOutputPortAssociationsGet,
)
from app.data_products.output_ports.input_ports.schema_response import BaseInputPortGet
from app.shared.schema import ORMModel
from app.users.enums import RequestTypes


class BaseUserGet(ORMModel):
    id: UUID
    email: EmailStr
    external_id: str
    first_name: str
    last_name: str
    has_seen_tour: bool
    can_become_admin: bool
    admin_expiry: Optional[datetime] = None


class UserGet(BaseUserGet):
    pass


class UsersGet(BaseUserGet):
    global_role: Optional[GlobalRoleAssignmentResponse]


class GetUsersResponse(ORMModel):
    users: Sequence[UsersGet]


class UserCreateResponse(ORMModel):
    id: UUID


class TechnicalAssetOutputPortRequest(TechnicalAssetOutputPortAssociationsGet):
    request_type: Literal[RequestTypes.TechnicalAssetOutputPort] = (
        RequestTypes.TechnicalAssetOutputPort
    )


class DataProductRoleAssignmentRequest(DataProductRoleAssignmentResponse):
    request_type: Literal[RequestTypes.DataProductRoleAssignment] = (
        RequestTypes.DataProductRoleAssignment
    )


class InputPortRequest(BaseInputPortGet):
    request_type: Literal[RequestTypes.InputPort] = RequestTypes.InputPort


Request = Union[
    InputPortRequest,
    TechnicalAssetOutputPortRequest,
    DataProductRoleAssignmentRequest,
]


class PendingActionResponse(ORMModel):
    pending_actions: Sequence[Request]


class MyRequestsResponse(ORMModel):
    my_requests: Sequence[Request]
