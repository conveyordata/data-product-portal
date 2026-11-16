from datetime import datetime, timedelta, timezone

from app.authorization.role_assignments.global_.service import RoleAssignmentService
from app.authorization.roles import ADMIN_UUID
from app.core.authz.authorization import Authorization
from tests.factories import GlobalRoleAssignmentFactory, UserFactory


class TestRoleAssignmentService:
    def test_become_admin__stores_expiry_in_utc(self, session):
        user = UserFactory(can_become_admin=True)
        expiry = datetime(2099, 1, 1, 2, 0, tzinfo=timezone(timedelta(hours=2)))

        RoleAssignmentService(session).become_admin(user, expiry)
        session.refresh(user)

        assert user.admin_expiry == datetime(2099, 1, 1, 0, 0)

    def test_revoke_admin__ends_temporary_admin(self, session):
        user = UserFactory(can_become_admin=True)
        service = RoleAssignmentService(session)
        service.become_admin(user, datetime(2099, 1, 1))

        service.revoke_admin(user)

        assert user.admin_expiry is None
        assert Authorization().has_admin_role(user_id=str(user.id)) is False
        assert service.is_admin(user.id) is False

    def test_revoke_admin__keeps_permanent_admin_role(self, session):
        user = UserFactory()
        GlobalRoleAssignmentFactory(identity_id=user.id, role_id=ADMIN_UUID)

        service = RoleAssignmentService(session)

        service.revoke_admin(user)

        assert Authorization().has_admin_role(user_id=str(user.id)) is True
        assert service.is_admin(user.id) is True
