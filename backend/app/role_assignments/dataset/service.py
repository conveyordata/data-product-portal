from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import ensure_exists
from app.role_assignments.dataset.model import DatasetRoleAssignment
from app.role_assignments.dataset.schema import (
    CreateRoleAssignment,
    RoleAssignment,
    UpdateRoleAssignment,
)
from app.role_assignments.enums import DecisionStatus
from app.users.schema import User


class RoleAssignmentService:
    def __init__(self, db: Session, user: User) -> None:
        self.db = db
        self.user = user

    def get_assignment(self, id_: UUID) -> RoleAssignment:
        return ensure_exists(id_, self.db, DatasetRoleAssignment)

    def list_assignments(
        self,
        *,
        dataset_id: Optional[UUID],
        user_id: Optional[UUID],
        decision: Optional[DecisionStatus] = None,
    ) -> Sequence[RoleAssignment]:
        query = select(DatasetRoleAssignment)
        if dataset_id is not None:
            query = query.where(DatasetRoleAssignment.dataset_id == dataset_id)
        if user_id is not None:
            query = query.where(DatasetRoleAssignment.user_id == user_id)
        if decision is not None:
            query = query.where(DatasetRoleAssignment.decision == decision)

        return self.db.scalars(query).all()

    def create_assignment(self, request: CreateRoleAssignment) -> RoleAssignment:
        role_assignment = DatasetRoleAssignment(
            **request.model_dump(),
            requested_on=datetime.now(),
            requested_by_id=self.user.id,
        )
        self.db.add(role_assignment)
        self.db.commit()
        return role_assignment

    def delete_assignment(self, id_: UUID) -> RoleAssignment:
        assignment = self.get_assignment(id_)
        self.db.delete(assignment)
        self.db.commit()
        return assignment

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
