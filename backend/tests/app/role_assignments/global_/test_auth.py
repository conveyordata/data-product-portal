from tests.factories import GlobalRoleAssignmentFactory, RoleFactory, UserFactory

from app.core.authz import Authorization
from app.role_assignments.dataset.schema import RoleAssignment
from app.role_assignments.enums import DecisionStatus
from app.role_assignments.global_.auth import GlobalAuthAssignment
from app.roles import ADMIN_UUID
from app.roles.schema import Role, Scope
from app.users.schema import User


class TestAuth:
    def test_add(self, authorizer: Authorization):
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)

        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        assert authorizer.has_global_role(user_id=str(user.id), role_id=str(role.id))

    def test_add_admin(self, authorizer: Authorization):
        user: User = UserFactory()
        admin: Role = RoleFactory(scope=Scope.GLOBAL, id=ADMIN_UUID)

        assignment: RoleAssignment = GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=admin.id,
            decision=DecisionStatus.APPROVED,
        )

        assert not authorizer.has_admin_role(user_id=str(user.id))
        GlobalAuthAssignment(assignment).add()
        assert authorizer.has_admin_role(user_id=str(user.id))

    def test_remove(self, authorizer: Authorization):
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)

        assignment: RoleAssignment = GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        # assert not authorizer.has_global_role(
        #     user_id=str(user.id), role_id=str(role.id)
        # )
        # GlobalAuthAssignment(assignment).add()
        assert authorizer.has_global_role(user_id=str(user.id), role_id=str(role.id))
        GlobalAuthAssignment(assignment).remove()
        assert not authorizer.has_global_role(
            user_id=str(user.id), role_id=str(role.id)
        )

    def test_remove_admin(self, authorizer: Authorization):
        user: User = UserFactory()
        admin: Role = RoleFactory(scope=Scope.GLOBAL, id=ADMIN_UUID)

        assignment: RoleAssignment = GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=admin.id,
            decision=DecisionStatus.APPROVED,
        )

        assert not authorizer.has_admin_role(user_id=str(user.id))
        GlobalAuthAssignment(assignment).add()
        assert authorizer.has_admin_role(user_id=str(user.id))
        GlobalAuthAssignment(assignment).remove()
        assert not authorizer.has_admin_role(user_id=str(user.id))

    def test_swap(self, authorizer: Authorization):
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        admin: Role = RoleFactory(scope=Scope.GLOBAL, id=ADMIN_UUID)

        assignment: RoleAssignment = GlobalRoleAssignmentFactory(
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
