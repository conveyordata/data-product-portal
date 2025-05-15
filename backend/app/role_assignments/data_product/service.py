from datetime import datetime
from http import HTTPStatus
from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import asc, func, select
from sqlalchemy.orm import Session

from app.core.authz import Action
from app.database.database import ensure_exists
from app.role_assignments.data_product.model import DataProductRoleAssignment
from app.role_assignments.data_product.schema import (
    CreateRoleAssignment,
    RoleAssignment,
    RoleAssignmentResponse,
    UpdateRoleAssignment,
)
from app.role_assignments.enums import DecisionStatus
from app.roles.model import Role
from app.roles.schema import Prototype
from app.users.schema import User


class RoleAssignmentService:
    def __init__(self, db: Session, user: User) -> None:
        self.db = db
        self.user = user

    def get_assignment(self, id_: UUID) -> RoleAssignment:
        return ensure_exists(id_, self.db, DataProductRoleAssignment)

    def list_assignments(
        self,
        *,
        data_product_id: Optional[UUID],
        user_id: Optional[UUID],
        decision: Optional[DecisionStatus] = None,
    ) -> Sequence[RoleAssignment]:
        query = select(DataProductRoleAssignment)
        if data_product_id is not None:
            query = query.where(
                DataProductRoleAssignment.data_product_id == data_product_id
            )
        if user_id is not None:
            query = query.where(DataProductRoleAssignment.user_id == user_id)
        if decision is not None:
            query = query.where(DataProductRoleAssignment.decision == decision)

        return self.db.scalars(query).all()

    def create_assignment(self, request: CreateRoleAssignment) -> RoleAssignment:
        role_assignment = DataProductRoleAssignment(
            **request.model_dump(),
            requested_on=datetime.now(),
            requested_by_id=self.user.id,
        )
        self.db.add(role_assignment)
        self.db.commit()
        return role_assignment

    def delete_assignment(self, id_: UUID) -> RoleAssignment:
        assignment = self.get_assignment(id_)

        if (
            assignment.role is not None
            and assignment.role.prototype == Prototype.OWNER
            and assignment.decision == DecisionStatus.APPROVED
            and self.count_owners(assignment.data_product_id) <= 1
        ):
            raise HTTPException(
                HTTPStatus.FORBIDDEN,
                "A data product must always be owned by at least one user",
            )

        self.db.delete(assignment)
        self.db.commit()
        return assignment

    def count_owners(self, data_product_id: UUID) -> int:
        query = (
            select(func.count())
            .select_from(DataProductRoleAssignment)
            .where(DataProductRoleAssignment.data_product_id == data_product_id)
            .join(Role)
            .where(Role.prototype == Prototype.OWNER)
        )
        return self.db.scalar(query)

    def update_assignment(self, request: UpdateRoleAssignment) -> RoleAssignment:
        assignment = self.get_assignment(request.id)

        if (role_id := request.role_id) is not None:
            assignment.role_id = role_id
        if (decision := request.decision) is not None:
            assignment.decision = decision
            assignment.decided_on = datetime.now()
            assignment.decided_by_id = self.user.id

        self.db.commit()
        return assignment

    def get_user_pending_data_product_assignments(
        self, authenticated_user: User
    ) -> Sequence[RoleAssignmentResponse]:
        data_product_ids = (
            select(DataProductRoleAssignment.data_product_id)
            .join(DataProductRoleAssignment.role)
            .where(
                DataProductRoleAssignment.user_id == authenticated_user.id,
                Role.permissions.contains(
                    [Action.DATA_PRODUCT__APPROVE_USER_REQUEST.value]
                ),
            )
            .scalar_subquery()
        )

        actions = (
            self.db.scalars(
                select(DataProductRoleAssignment)
                .filter(DataProductRoleAssignment.decision == DecisionStatus.PENDING)
                .filter(DataProductRoleAssignment.data_product_id.in_(data_product_ids))
                .order_by(asc(DataProductRoleAssignment.requested_on))
            )
            .unique()
            .all()
        )
        return actions
