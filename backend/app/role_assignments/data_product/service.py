from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.role_assignments.data_product.model import DataProductRoleAssignment
from app.role_assignments.data_product.schema import (
    CreateRoleAssignment,
    RoleAssignment,
)
from app.users.schema import User


class RoleAssignmentService:
    def __init__(self, db: Session, user: User) -> None:
        self.db = db
        self.user = user

    def list_assignments(
        self, data_product_id: Optional[UUID], user_id: Optional[UUID]
    ) -> Sequence[RoleAssignment]:
        query = select(DataProductRoleAssignment)
        if data_product_id is not None:
            query = query.where(
                DataProductRoleAssignment.data_product_id == data_product_id
            )
        if user_id is not None:
            query = query.where(DataProductRoleAssignment.user_id == user_id)

        return self.db.scalars(
            query.order_by(
                DataProductRoleAssignment.data_product.name.asc(),
                DataProductRoleAssignment.user.last_name.asc(),
                DataProductRoleAssignment.user.first_name.asc(),
            )
        ).all()

    def create_assignments(self, request: CreateRoleAssignment) -> RoleAssignment:
        role_assignment = DataProductRoleAssignment(
            **request, requested_by_id=self.user.id, requested_on=datetime.now()
        )
        self.db.add(role_assignment)
        self.db.commit()
        return role_assignment
