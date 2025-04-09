from datetime import datetime
from typing import Optional, cast
from uuid import UUID

from casbin_async_sqlalchemy_adapter import CasbinRule
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.data_product_memberships.enums import (
    DataProductMembershipStatus,
    DataProductUserRole,
)
from app.data_product_memberships.schema import DataProductMembership
from app.data_product_memberships.service import DataProductMembershipService
from app.database.database import get_db_session
from app.datasets.model import Dataset
from app.role_assignments.data_product import tasks as data_product_tasks
from app.role_assignments.data_product.model import DataProductRoleAssignment
from app.role_assignments.data_product.service import (
    RoleAssignmentService as DataProductRoleAssignmentService,
)
from app.role_assignments.data_product.tasks import (
    AuthAssignment as DataProductAuthAssignment,
)
from app.role_assignments.dataset import tasks as dataset_tasks
from app.role_assignments.dataset.model import DatasetRoleAssignment
from app.role_assignments.dataset.service import (
    RoleAssignmentService as DatasetRoleAssignmentService,
)
from app.role_assignments.dataset.tasks import AuthAssignment as DatasetAuthAssignment
from app.role_assignments.enums import DecisionStatus
from app.role_assignments.global_ import tasks as global_tasks
from app.role_assignments.global_.model import GlobalRoleAssignment
from app.role_assignments.global_.service import (
    RoleAssignmentService as GlobalRoleAssignmentService,
)
from app.role_assignments.global_.tasks import AuthAssignment as GlobalAuthAssignment
from app.roles.model import Role
from app.roles.schema import CreateRole, Prototype, Scope
from app.roles.service import RoleService
from app.users.model import User as UserModel
from app.users.schema import User


async def migrate():
    db = next(get_db_session())

    transfer_product_memberships(db)
    transfer_dataset_memberships(db)
    transfer_global_memberships(db)

    await sync_casbin(db)


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
    if membership.status == DataProductMembershipStatus.APPROVED:
        return DecisionStatus.APPROVED, membership.approved_by, membership.approved_on
    if membership.status == DataProductMembershipStatus.DENIED:
        return DecisionStatus.DENIED, membership.declined_by, membership.denied_on
    if membership.status == DataProductMembershipStatus.PENDING_APPROVAL:
        return DecisionStatus.PENDING, None, None
    raise ValueError("Invalid membership status")


def transfer_dataset_memberships(db: Session):
    role = RoleService(db).find_prototype(Scope.DATASET, Prototype.OWNER)
    role_id = None
    if role:
        role_id = role.id
    datasets = db.scalars(select(Dataset)).all()
    for dataset in datasets:
        for owner in dataset.owners:
            db.add(
                DatasetRoleAssignment(
                    dataset_id=dataset.id,
                    user_id=owner.id,
                    role_id=role_id,
                    decision=DecisionStatus.APPROVED,
                    requested_on=dataset.updated_on,
                    decided_on=dataset.updated_on,
                )
            )
    db.commit()


def transfer_global_memberships(db: Session):
    role = RoleService(db).find_prototype(Scope.GLOBAL, Prototype.ADMIN)
    role_id = None
    if role:
        role_id = role.id
    users = db.scalars(select(UserModel)).all()
    for user in users:
        if user.is_admin:
            db.add(
                GlobalRoleAssignment(
                    user_id=user.id,
                    role_id=role_id,
                    decision=DecisionStatus.APPROVED,
                    requested_on=user.updated_on,
                    decided_on=user.updated_on,
                )
            )
    db.commit()


async def sync_casbin(db: Session):
    clear_casbin_groups(db)

    await sync_product_assignments(db)
    await sync_dataset_assignments(db)
    await sync_global_assignments(db)


def clear_casbin_groups(db: Session):
    # We only remove the group permissions, role permissions ('p') are untouched
    db.execute(delete(CasbinRule).where(CasbinRule.ptype.in_(["g", "g2", "g3"])))


async def sync_product_assignments(db: Session):
    service = DataProductRoleAssignmentService(db, cast(User, None))
    product_assignments = service.list_assignments(data_product_id=None, user_id=None)

    for assignment in product_assignments:
        await data_product_tasks.add_assignment(
            DataProductAuthAssignment.from_data_product(assignment)
        )


async def sync_dataset_assignments(db: Session):
    service = DatasetRoleAssignmentService(db, cast(User, None))
    dataset_assignments = service.list_assignments(dataset_id=None, user_id=None)

    for assignment in dataset_assignments:
        await dataset_tasks.add_assignment(
            DatasetAuthAssignment.from_dataset(assignment)
        )


async def sync_global_assignments(db: Session):
    service = GlobalRoleAssignmentService(db, cast(User, None))
    global_assignments = service.list_assignments(user_id=None)

    for assignment in global_assignments:
        await global_tasks.add_assignment(GlobalAuthAssignment.from_global(assignment))


if __name__ == "__main__":
    migrate()
