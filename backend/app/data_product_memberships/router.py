from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import (
    Action,
    Authorization,
    DataProductMembershipResolver,
    DataProductResolver,
)
from app.data_product_memberships.enums import DataProductUserRole
from app.data_product_memberships.model import DataProductMembership
from app.data_product_memberships.schema import DataProductMembershipCreate
from app.data_product_memberships.schema_get import DataProductMembershipGet
from app.data_product_memberships.service import DataProductMembershipService
from app.database.database import get_db_session
from app.dependencies import (
    OnlyWithProductAccessDataProductID,
    only_product_membership_owners,
)
from app.role_assignments.data_product.router import (
    list_assignments,
    modify_assigned_role,
)
from app.role_assignments.data_product.schema import ModifyRoleAssignment
from app.roles.model import Role
from app.roles.schema import Scope
from app.users.schema import User

router = APIRouter(
    prefix="/data_product_memberships", tags=["data_product_memberships"]
)


@router.post(
    "/create",
    dependencies=[
        Depends(OnlyWithProductAccessDataProductID([DataProductUserRole.OWNER])),
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__CREATE_USER,
                DataProductResolver,
                object_id="data_product_id",
            )
        ),
    ],
)
def create_data_product_membership(
    data_product_id: UUID,
    data_product_membership: DataProductMembershipCreate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return DataProductMembershipService().add_data_product_membership(
        data_product_id, data_product_membership, db, authenticated_user
    )


@router.post(
    "/request",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__REQUEST_DATAPRODUCT_ACCESS,
                DataProductResolver,
                object_id="data_product_id",
            )
        )
    ],
)
def request_data_product_membership(
    user_id: UUID,
    data_product_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return DataProductMembershipService().request_user_access_to_data_product(
        user_id, data_product_id, authenticated_user, db, background_tasks
    )


@router.post(
    "/{id}/approve",
    dependencies=[
        Depends(only_product_membership_owners),
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__APPROVE_USER_REQUEST,
                DataProductMembershipResolver,
            )
        ),
    ],
)
def approve_data_product_membership(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return DataProductMembershipService().approve_membership_request(
        id, db, authenticated_user
    )


@router.post(
    "/{id}/deny",
    dependencies=[
        Depends(only_product_membership_owners),
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__APPROVE_USER_REQUEST,
                DataProductMembershipResolver,
            )
        ),
    ],
)
def deny_data_product_membership(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return DataProductMembershipService().deny_membership_request(
        id, db, authenticated_user
    )


@router.post(
    "/{id}/remove",
    dependencies=[
        Depends(only_product_membership_owners),
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__DELETE_USER,
                DataProductMembershipResolver,
            )
        ),
    ],
)
def remove_data_product_membership(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return DataProductMembershipService().remove_membership(id, db, authenticated_user)


@router.put(
    "/{id}/role",
    responses={
        400: {
            "description": "Role not found",
            "content": {"application/json": {"example": {"detail": "Role not found"}}},
        },
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        },
    },
    dependencies=[
        Depends(only_product_membership_owners),
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__UPDATE_USER,
                DataProductMembershipResolver,
            )
        ),
    ],
)
def update_data_product_role(
    id: UUID,
    membership_role: DataProductUserRole,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    old_membership = db.scalar(select(DataProductMembership).filter_by(id=id))
    old_role = old_membership.role.name.lower()
    updated_id = DataProductMembershipService().update_data_product_membership_role(
        id, membership_role, db
    )
    roles = list_assignments(
        old_membership.data_product_id, old_membership.user_id, db, authenticated_user
    )
    for role in roles:
        if role.role.name.lower() == old_role:
            new_role = db.scalar(
                select(Role)
                .filter_by(scope=Scope.DATA_PRODUCT)
                .filter(func.lower(Role.name) == membership_role.name.lower())
            )
            request = ModifyRoleAssignment(role_id=new_role.id)
            modify_assigned_role(
                role.id, request, background_tasks, db, authenticated_user
            )
    return {"id": updated_id}


@router.get("/actions")
def get_user_pending_actions(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> list[DataProductMembershipGet]:
    return DataProductMembershipService().get_user_pending_actions(
        db, authenticated_user
    )
