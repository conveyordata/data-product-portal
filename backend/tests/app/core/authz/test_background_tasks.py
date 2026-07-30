import asyncio
from datetime import datetime, timedelta, timezone

from app.core.authz.authorization import Authorization
from app.core.authz.background_tasks import revoke_expired_admins
from tests import test_session
from tests.factories import UserFactory

NOW = datetime.now(timezone.utc)


class TestRevokeExpiredAdmins:
    def test_revoke_expired_admins__lapsed_expiry_revokes_role_and_clears_expiry(
        self, authorizer: Authorization
    ):
        user = UserFactory(admin_expiry=NOW - timedelta(days=1))
        test_session.commit()
        authorizer.assign_admin_role(user_id=user.id)

        asyncio.run(revoke_expired_admins(test_session))

        test_session.refresh(user)
        assert authorizer.has_admin_role(user_id=user.id) is False
        assert user.admin_expiry is None

    def test_revoke_expired_admins__future_expiry_is_untouched(
        self, authorizer: Authorization
    ):
        user = UserFactory(admin_expiry=NOW + timedelta(days=1))
        test_session.commit()
        authorizer.assign_admin_role(user_id=user.id)

        asyncio.run(revoke_expired_admins(test_session))

        test_session.refresh(user)
        assert authorizer.has_admin_role(user_id=user.id) is True
        assert user.admin_expiry is not None

    def test_revoke_expired_admins__no_expiry_is_ignored(
        self, authorizer: Authorization
    ):
        user = UserFactory(admin_expiry=None)
        test_session.commit()
        authorizer.assign_admin_role(user_id=user.id)

        asyncio.run(revoke_expired_admins(test_session))

        test_session.refresh(user)
        assert authorizer.has_admin_role(user_id=user.id) is True
        assert user.admin_expiry is None
