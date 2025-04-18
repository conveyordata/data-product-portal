"""migrate RBAC

Revision ID: 6fd335d0dcfe
Revises: b3a391db07dd
Create Date: 2025-04-16 16:58:38.284751

"""

import asyncio
from datetime import datetime
from typing import Optional, Sequence, Union
from uuid import UUID

import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import Session

from app.authorization.service import AuthorizationService
from app.core.authz import Action, Authorization
from app.data_product_memberships.enums import (
    DataProductMembershipStatus,
    DataProductUserRole,
)
from app.data_product_memberships.schema import DataProductMembership
from app.data_product_memberships.service import DataProductMembershipService
from app.datasets.model import Dataset
from app.role_assignments.data_product.model import DataProductRoleAssignment
from app.role_assignments.dataset.model import DatasetRoleAssignment
from app.role_assignments.enums import DecisionStatus
from app.role_assignments.global_.model import GlobalRoleAssignment
from app.roles import ADMIN_UUID
from app.roles.model import Role as RoleModel
from app.roles.schema import CreateRole, Prototype, Role, Scope
from app.roles.service import RoleService
from app.users.model import User as UserModel

# revision identifiers, used by Alembic.
revision: str = "6fd335d0dcfe"
down_revision: Union[str, None] = "b3a391db07dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class RoleMigrationService:
    def __init__(self, db: Session):
        self.db = db
        self.role_service = RoleService(db)

    async def migrate(self):
        self._transfer_product_memberships()
        self._transfer_dataset_memberships()
        self._transfer_global_memberships()

        await Authorization.initialize()
        auth_service = AuthorizationService(db=self.db)
        await auth_service.reload_enforcer()
        Authorization.deregister()

    def _transfer_product_memberships(self):
        memberships = DataProductMembershipService().list_memberships(self.db)

        owner_role = self.role_service.find_prototype(Scope.DATA_PRODUCT, Prototype.OWNER)
        assert owner_role is not None

        # Create the member role if it doesn't exist
        member_role = self.db.scalars(
            sa.select(RoleModel).filter_by(name="Member", scope=Scope.DATA_PRODUCT)
        ).one_or_none()
        if member_role is None:
            member_role = self.role_service.create_role(
                CreateRole(
                    name="Member",
                    scope=Scope.DATA_PRODUCT,
                    description="A member of the data product",
                    permissions=[
                        Action.DATA_PRODUCT__REQUEST_DATA_OUTPUT_LINK,
                        Action.DATA_PRODUCT__REQUEST_DATASET_ACCESS,
                        Action.DATA_PRODUCT__READ_INTEGRATIONS,
                    ],
                )
            )

        for membership in memberships:
            role_id = (
                owner_role.id
                if membership.role == DataProductUserRole.OWNER
                else member_role.id
            )
            decision, decided_by, decided_on = self.map_decision(membership)
            self.db.add(
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
        self.db.commit()

    @classmethod
    def map_decision(
        cls,
        membership: DataProductMembership,
    ) -> tuple[DecisionStatus, Optional[UUID], Optional[datetime]]:
        if membership.status == DataProductMembershipStatus.APPROVED:
            return (
                DecisionStatus.APPROVED,
                membership.approved_by,
                membership.approved_on,
            )
        if membership.status == DataProductMembershipStatus.DENIED:
            return DecisionStatus.DENIED, membership.declined_by, membership.denied_on
        if membership.status == DataProductMembershipStatus.PENDING_APPROVAL:
            return DecisionStatus.PENDING, None, None
        raise ValueError("Invalid membership status")

    def _transfer_dataset_memberships(self):
        owner_role = self.role_service.find_prototype(Scope.DATASET, Prototype.OWNER)
        assert owner_role is not None

        datasets = self.db.scalars(sa.select(Dataset)).all()
        for dataset in datasets:
            for owner in dataset.owners:
                self.db.add(
                    DatasetRoleAssignment(
                        dataset_id=dataset.id,
                        user_id=owner.id,
                        role_id=owner_role.id,
                        decision=DecisionStatus.APPROVED,
                        requested_on=dataset.updated_on,
                        decided_on=dataset.updated_on,
                    )
                )
        self.db.commit()

    def _transfer_global_memberships(self):
        admin_role = self.role_service.find_prototype(Scope.GLOBAL, Prototype.ADMIN)
        assert admin_role is not None

        users = self.db.scalars(sa.select(UserModel)).all()
        for user in users:
            if user.is_admin:
                self.db.add(
                    GlobalRoleAssignment(
                        user_id=user.id,
                        role_id=admin_role.id,
                        decision=DecisionStatus.APPROVED,
                        requested_on=user.updated_on,
                        decided_on=user.updated_on,
                    )
                )
        self.db.commit()


def upgrade() -> None:
    session = Session(bind=op.get_bind())

    service = RoleMigrationService(db=session)
    service.role_service.initialize_prototype_roles()
    asyncio.run(service.migrate())


def downgrade() -> None:
    session = Session(bind=op.get_bind())
    session.execute(sa.delete(DataProductRoleAssignment))
    session.execute(sa.delete(DatasetRoleAssignment))
    session.execute(sa.delete(GlobalRoleAssignment))
    session.commit()
