from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.authorization.service import AuthorizationService
from app.core.authz import Authorization
from app.data_product_memberships.enums import (
    DataProductUserRole,
)
from app.data_product_memberships.schema import DataProductMembership
from app.data_product_memberships.service import DataProductMembershipService
from app.database.database import get_db_session
from app.datasets.model import Dataset
from app.role_assignments.data_product.model import DataProductRoleAssignment
from app.role_assignments.dataset.model import DatasetRoleAssignment
from app.role_assignments.enums import DecisionStatus
from app.role_assignments.global_.model import GlobalRoleAssignment
from app.roles.model import Role
from app.roles.schema import CreateRole, Prototype, Scope
from app.roles.service import RoleService
from app.users.model import User as UserModel


async def migrate():
    db = next(get_db_session())

    transfer_product_memberships(db)
    transfer_dataset_memberships(db)
    transfer_global_memberships(db)

    auth_service = AuthorizationService(db=db, authorizer=Authorization())
    await auth_service.reload_enforcer()


def transfer_product_memberships(db: Session):
    memberships = DataProductMembershipService().list_memberships(db)

    owner_role = RoleService(db).find_prototype(Scope.DATA_PRODUCT, Prototype.OWNER)
    assert owner_role is not None

    # Create the member role if it doesn't exist
    member_role = db.scalars(
        select(Role).filter_by(name="Member", scope=Scope.DATA_PRODUCT)
    ).one_or_none()
    if member_role is None:
        member_role = RoleService(db).create_role(
            CreateRole(
                name="Member",
                scope=Scope.DATA_PRODUCT,
                description="A member of the data product",
                permissions=[],
            )
        )

    for membership in memberships:
        role_id = (
            owner_role.id
            if membership.role == DataProductUserRole.OWNER
            else member_role.id
        )
        decision, decided_by, decided_on = map_decision(membership)
        db.add(
            DataProductRoleAssignment(
                data_product_id=membership.data_product_id,
                user_id=membership.user_id,
                role_id=role_id,
                requested_on=membership.requested_on,
                requested_by_id=membership.requested_by_id,
                decision=decision,
                decided_on=decided_on,
                decided_by=decided_by,
            )
        )
    db.commit()


def map_decision(
    membership: DataProductMembership,
) -> tuple[DecisionStatus, Optional[UUID], Optional[datetime]]:
    if membership.status == DecisionStatus.APPROVED:
        return DecisionStatus.APPROVED, membership.approved_by, membership.approved_on
    if membership.status == DecisionStatus.DENIED:
        return DecisionStatus.DENIED, membership.declined_by, membership.denied_on
    if membership.status == DecisionStatus.PENDING:
        return DecisionStatus.PENDING, None, None
    raise ValueError("Invalid membership status")


def transfer_dataset_memberships(db: Session):
    owner_role = RoleService(db).find_prototype(Scope.DATASET, Prototype.OWNER)
    assert owner_role is not None

    datasets = db.scalars(select(Dataset)).all()
    for dataset in datasets:
        for owner in dataset.owners:
            db.add(
                DatasetRoleAssignment(
                    dataset_id=dataset.id,
                    user_id=owner.id,
                    role_id=owner_role.id,
                    decision=DecisionStatus.APPROVED,
                    requested_on=dataset.updated_on,
                    decided_on=dataset.updated_on,
                )
            )
    db.commit()


def transfer_global_memberships(db: Session):
    admin_role = RoleService(db).find_prototype(Scope.GLOBAL, Prototype.ADMIN)
    assert admin_role is not None

    users = db.scalars(select(UserModel)).all()
    for user in users:
        if user.is_admin:
            db.add(
                GlobalRoleAssignment(
                    user_id=user.id,
                    role_id=admin_role.id,
                    decision=DecisionStatus.APPROVED,
                    requested_on=user.updated_on,
                    decided_on=user.updated_on,
                )
            )
    db.commit()


if __name__ == "__main__":
    migrate()
