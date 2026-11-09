from uuid import UUID

from sqlalchemy import ColumnElement, or_, select

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.global_.model import GlobalRoleAssignment
from app.authorization.roles import ADMIN_UUID
from app.shared.model import utcnow
from app.users.model import User

admin_expiry_in_future = User.admin_expiry > utcnow()


def is_user_admin(user_id: UUID) -> ColumnElement[bool]:
    temporary = (
        select(User.id)
        .where(User.id == user_id, admin_expiry_in_future)
        .correlate(None)
        .exists()
    )
    permanent = (
        select(GlobalRoleAssignment.id)
        .where(
            GlobalRoleAssignment.identity_id == user_id,
            GlobalRoleAssignment.role_id == ADMIN_UUID,
            GlobalRoleAssignment.decision == DecisionStatus.APPROVED,
        )
        .correlate(None)
        .exists()
    )
    return or_(temporary, permanent)
