"""migrate RBAC

Revision ID: 6fd335d0dcfe
Revises: b3a391db07dd
Create Date: 2025-04-16 16:58:38.284751

"""

from datetime import datetime
from enum import Enum
from typing import Optional, Sequence, Union
from uuid import UUID

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Session

from app.authorization.service import AuthorizationService
from app.core.authz import Action, Authorization
from app.datasets.model import Dataset
from app.role_assignments.data_product.model import DataProductRoleAssignment
from app.role_assignments.dataset.model import DatasetRoleAssignment
from app.role_assignments.enums import DecisionStatus
from app.role_assignments.global_.model import GlobalRoleAssignment
from app.roles.model import Role as RoleModel
from app.roles.schema import CreateRole, Prototype, Scope
from app.roles.service import RoleService

# revision identifiers, used by Alembic.
revision: str = "6fd335d0dcfe"
down_revision: Union[str, None] = "b3a391db07dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

data_product_membership = sa.Table(
    "data_product_memberships",
    sa.MetaData(),
    sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
    sa.Column(
        "user_id", PGUUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
    ),
    sa.Column(
        "data_product_id",
        PGUUID(as_uuid=True),
        sa.ForeignKey("data_products.id"),
        nullable=False,
    ),
    sa.Column("role", sa.String, nullable=False),
    sa.Column("status", sa.String, nullable=False),
    sa.Column("requested_on", sa.DateTime, nullable=False),
    sa.Column(
        "requested_by_id",
        PGUUID(as_uuid=True),
        sa.ForeignKey("users.id"),
        nullable=True,
    ),
    sa.Column(
        "approved_by_id", PGUUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True
    ),
    sa.Column("approved_on", sa.DateTime, nullable=True),
    sa.Column(
        "denied_by_id", PGUUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True
    ),
    sa.Column("denied_on", sa.DateTime, nullable=True),
)


# Define DataProductMembershipStatus enum
class DataProductMembershipStatus(str, Enum):
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    PENDING_APPROVAL = "PENDING_APPROVAL"


# Define DataProductUserRole enum
class DataProductUserRole(str, Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class RoleMigrationService:
    def __init__(self, db: Session, data_product_membership):
        self.db = db
        self.role_service = RoleService(db)
        self.data_product_membership = data_product_membership

    def migrate(self):
        self._transfer_product_memberships()
        self._transfer_dataset_memberships()
        self._transfer_global_memberships()

        AuthorizationService(self.db).reload_enforcer()
        Authorization.deregister()

    def _transfer_product_memberships(self):
        memberships = self.db.execute(
            sa.select(self.data_product_membership)
        ).fetchall()

        owner_role = self.role_service.find_prototype(
            Scope.DATA_PRODUCT, Prototype.OWNER
        )
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
            decision, decided_by_id, decided_on = self.map_decision(membership)
            self.db.add(
                DataProductRoleAssignment(
                    data_product_id=membership.data_product_id,
                    user_id=membership.user_id,
                    role_id=role_id,
                    requested_on=membership.requested_on,
                    requested_by_id=membership.requested_by_id,
                    decision=decision,
                    decided_on=decided_on,
                    decided_by_id=decided_by_id,
                )
            )
        self.db.commit()

    @classmethod
    def map_decision(
        cls, membership  #: DataProductMembership,
    ) -> tuple[DecisionStatus, Optional[UUID], Optional[datetime]]:
        if membership.status == DataProductMembershipStatus.APPROVED:
            return (
                DecisionStatus.APPROVED,
                membership.approved_by_id,
                membership.approved_on,
            )
        if membership.status == DataProductMembershipStatus.DENIED:
            return (
                DecisionStatus.DENIED,
                membership.declined_by_id,
                membership.denied_on,
            )
        if membership.status == DataProductMembershipStatus.PENDING_APPROVAL:
            return DecisionStatus.PENDING, None, None
        raise ValueError("Invalid membership status")

    def _transfer_dataset_memberships(self):
        owner_role = self.role_service.find_prototype(Scope.DATASET, Prototype.OWNER)
        assert owner_role is not None

        datasets = self.db.scalars(sa.select(Dataset)).unique().all()
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

        users = self.db.execute(sa.sql.text("""select * from users""")).all()
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
    metadata = sa.MetaData()
    metadata.reflect(bind=session.bind)

    data_product_membership = metadata.tables["data_product_memberships"]

    service = RoleMigrationService(
        db=session, data_product_membership=data_product_membership
    )
    service.role_service.initialize_prototype_roles()
    service.migrate()


def downgrade() -> None:
    session = Session(bind=op.get_bind())
    session.execute(sa.delete(DataProductRoleAssignment))
    session.execute(sa.delete(DatasetRoleAssignment))
    session.execute(sa.delete(GlobalRoleAssignment))
    session.commit()
