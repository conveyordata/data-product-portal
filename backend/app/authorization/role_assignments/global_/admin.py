from uuid import UUID

from sqlalchemy import ColumnElement, CompoundSelect, Select, or_, select, union
from sqlalchemy.orm import InstrumentedAttribute

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.global_.model import GlobalRoleAssignment
from app.authorization.roles import ADMIN_UUID
from app.shared.model import utcnow
from app.users.model import User

admin_expiry_in_future = User.admin_expiry > utcnow()


def is_admin_role(role_id: InstrumentedAttribute[UUID]) -> ColumnElement[bool]:
    return role_id == ADMIN_UUID


def admin_identity_ids() -> CompoundSelect[UUID]:
    return union(_temporary_admins(), _permanent_admins())


def is_user_admin(user_id: UUID) -> ColumnElement[bool]:
    return or_(
        _temporary_admins().where(User.id == user_id).correlate(None).exists(),
        _permanent_admins()
        .where(GlobalRoleAssignment.identity_id == user_id)
        .correlate(None)
        .exists(),
    )


def _temporary_admins() -> Select[UUID]:
    return select(User.id).where(admin_expiry_in_future)


def _permanent_admins() -> Select[UUID]:
    return select(GlobalRoleAssignment.identity_id).where(
        is_admin_role(GlobalRoleAssignment.role_id),
        GlobalRoleAssignment.decision == DecisionStatus.APPROVED,
    )
