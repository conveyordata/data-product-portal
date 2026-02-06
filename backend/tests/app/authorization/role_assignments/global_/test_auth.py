from typing import TYPE_CHECKING

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.global_.auth import GlobalAuthAssignment
from app.authorization.roles import ADMIN_UUID
from app.authorization.roles.schema import Role, Scope
from app.core.authz import Authorization
from tests.factories import GlobalRoleAssignmentFactory, RoleFactory, UserFactory

if TYPE_CHECKING:
    from app.authorization.role_assignments.global_.schema import GlobalRoleAssignment
    from app.users.schema import User


class TestAuth:
    def test_add(self, authorizer: Authorization):
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        assert not authorizer.has_global_role(
            user_id=str(user.id), role_id=str(role.id)
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        assert authorizer.has_global_role(user_id=str(user.id), role_id=str(role.id))

    def test_add_admin(self, authorizer: Authorization):
        user: User = UserFactory()
        admin: Role = RoleFactory(scope=Scope.GLOBAL, id=ADMIN_UUID)
        assert not authorizer.has_admin_role(user_id=str(user.id))
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=admin.id,
            decision=DecisionStatus.APPROVED,
        )
        assert authorizer.has_admin_role(user_id=str(user.id))

    def test_remove(self, authorizer: Authorization):
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        assert not authorizer.has_global_role(
            user_id=str(user.id), role_id=str(role.id)
        )
        assignment: GlobalRoleAssignment = GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        assert authorizer.has_global_role(user_id=str(user.id), role_id=str(role.id))
        GlobalAuthAssignment(assignment).remove()
        assert not authorizer.has_global_role(
            user_id=str(user.id), role_id=str(role.id)
        )

    def test_remove_admin(self, authorizer: Authorization):
        user: User = UserFactory()
        admin: Role = RoleFactory(scope=Scope.GLOBAL, id=ADMIN_UUID)
        assert not authorizer.has_admin_role(user_id=str(user.id))
        assignment: GlobalRoleAssignment = GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=admin.id,
            decision=DecisionStatus.APPROVED,
        )

        assert authorizer.has_admin_role(user_id=str(user.id))
        GlobalAuthAssignment(assignment).remove()
        assert not authorizer.has_admin_role(user_id=str(user.id))

    def test_swap(self, authorizer: Authorization):
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        admin: Role = RoleFactory(scope=Scope.GLOBAL, id=ADMIN_UUID)

        assignment: GlobalRoleAssignment = GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        GlobalAuthAssignment(assignment).add()
        assert authorizer.has_global_role(user_id=str(user.id), role_id=str(role.id))
        assert not authorizer.has_admin_role(user_id=str(user.id))

        assignment.role_id = admin.id
        GlobalAuthAssignment(assignment, previous_role_id=role.id).swap()

        assert not authorizer.has_global_role(
            user_id=str(user.id), role_id=str(role.id)
        )
        assert authorizer.has_admin_role(user_id=str(user.id))
