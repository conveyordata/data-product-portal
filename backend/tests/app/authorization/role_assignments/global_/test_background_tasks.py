import asyncio
from datetime import datetime, timedelta, timezone

from app.authorization.role_assignments.global_.background_tasks import (
    revoke_expired_admins,
)
from app.authorization.role_assignments.global_.service import RoleAssignmentService
from app.authorization.roles import ADMIN_UUID
from app.core.authz.authorization import Authorization
from tests.factories import GlobalRoleAssignmentFactory, UserFactory

NOW = datetime.now(timezone.utc)


class TestRevokeExpiredAdmins:
    def test_revoke_expired_admins__lapsed_expiry_revokes_role_and_clears_expiry(
        self, authorizer: Authorization, session
    ):
        user = UserFactory(admin_expiry=NOW - timedelta(days=1))
        authorizer.assign_admin_role(user_id=user.id)

        asyncio.run(revoke_expired_admins(session))

        session.refresh(user)
        assert authorizer.has_admin_role(user_id=user.id) is False
        assert user.admin_expiry is None
        assert RoleAssignmentService(session).is_admin(user.id) is False

    def test_revoke_expired_admins__keeps_permanent_admin_role(
        self, authorizer: Authorization, session
    ):
        user = UserFactory(admin_expiry=NOW - timedelta(days=1))
        GlobalRoleAssignmentFactory(identity_id=user.id, role_id=ADMIN_UUID)

        asyncio.run(revoke_expired_admins(session))

        session.refresh(user)
        assert authorizer.has_admin_role(user_id=str(user.id)) is True
        assert user.admin_expiry is None
        assert RoleAssignmentService(session).is_admin(user.id) is True

    def test_revoke_expired_admins__future_expiry_is_untouched(
        self,
        authorizer: Authorization,
        session,
    ):
        user = UserFactory(admin_expiry=NOW + timedelta(days=1))
        authorizer.assign_admin_role(user_id=user.id)

        asyncio.run(revoke_expired_admins(session))

        session.refresh(user)
        assert authorizer.has_admin_role(user_id=user.id) is True
        assert user.admin_expiry is not None

    def test_revoke_expired_admins__no_expiry_is_ignored(
        self,
        authorizer: Authorization,
        session,
    ):
        user = UserFactory(admin_expiry=None)
        authorizer.assign_admin_role(user_id=user.id)

        asyncio.run(revoke_expired_admins(session))

        session.refresh(user)
        assert authorizer.has_admin_role(user_id=user.id) is True
        assert user.admin_expiry is None
