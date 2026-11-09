from sqlalchemy import select

from app.authorization.role_assignments.global_.service import RoleAssignmentService
from app.authorization.roles import ADMIN_UUID
from app.core.authz.authorization import Authorization
from app.database.visibility import is_user_admin
from tests.factories import GlobalRoleAssignmentFactory, UserFactory


class TestRoleAssignmentService:
    def test_revoke_admin__ends_temporary_admin(self, session):
        user = UserFactory(can_become_admin=True)
        service = RoleAssignmentService(session)
        service.become_admin(user, "2099-01-01T00:00:00")

        service.revoke_admin(user)

        assert user.admin_expiry is None
        assert Authorization().has_admin_role(user_id=str(user.id)) is False
        assert session.scalar(select(is_user_admin(user.id))) is False

    def test_revoke_admin__keeps_permanent_admin_role(self, session):
        user = UserFactory()
        GlobalRoleAssignmentFactory(identity_id=user.id, role_id=ADMIN_UUID)

        RoleAssignmentService(session).revoke_admin(user)

        assert Authorization().has_admin_role(user_id=str(user.id)) is True
        assert session.scalar(select(is_user_admin(user.id))) is True
