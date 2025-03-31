from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import ensure_exists
from app.role_assignments.global_.model import GlobalRoleAssignment
from app.role_assignments.global_.schema import (
    RoleAssignment,
    RoleAssignmentRequest,
    UpdateRoleAssignment,
)
from app.users.schema import User

ADMIN_UUID = UUID(int=0)


class RoleAssignmentService:
    def __init__(self, db: Session, user: User) -> None:
        self.db = db
        self.user = user

    def get_assignment(self, id_: UUID) -> RoleAssignment:
        return ensure_exists(id_, self.db, GlobalRoleAssignment)

    def list_assignments(self, *, user_id: Optional[UUID]) -> Sequence[RoleAssignment]:
        query = select(GlobalRoleAssignment)
        if user_id is not None:
            query = query.where(GlobalRoleAssignment.user_id == user_id)

        return self.db.scalars(query).all()

    def create_assignment(self, request: RoleAssignmentRequest) -> RoleAssignment:
        role_assignment = GlobalRoleAssignment(
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
