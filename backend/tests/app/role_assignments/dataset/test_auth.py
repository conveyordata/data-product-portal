from tests.factories import (
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

from app.core.authz import Authorization
from app.datasets.model import Dataset
from app.role_assignments.dataset.auth import DatasetAuthAssignment
from app.role_assignments.dataset.schema import RoleAssignment
from app.role_assignments.enums import DecisionStatus
from app.roles.schema import Role, Scope
from app.users.schema import User


class TestAuth:
    def test_add(self, authorizer: Authorization):
        dataset: Dataset = DatasetFactory()
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATASET)

        assignment: RoleAssignment = DatasetRoleAssignmentFactory(
            dataset_id=dataset.id,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        assert not authorizer.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(dataset.id)
        )
        DatasetAuthAssignment(assignment).add()
        assert authorizer.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(dataset.id)
        )

    def test_remove(self, authorizer: Authorization):
        dataset: Dataset = DatasetFactory()
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATASET)

        assignment: RoleAssignment = DatasetRoleAssignmentFactory(
            dataset_id=dataset.id,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        assert not authorizer.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(dataset.id)
        )
        DatasetAuthAssignment(assignment).add()
        assert authorizer.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(dataset.id)
        )
        DatasetAuthAssignment(assignment).remove()
        assert not authorizer.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(dataset.id)
        )

    def test_swap(self, authorizer: Authorization):
        dataset: Dataset = DatasetFactory()
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATASET)
        new_role: Role = RoleFactory(scope=Scope.DATASET)

        assignment: RoleAssignment = DatasetRoleAssignmentFactory(
            dataset_id=dataset.id,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        DatasetAuthAssignment(assignment).add()
        assert authorizer.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(dataset.id)
        )

        assignment.role_id = new_role.id
        DatasetAuthAssignment(assignment, previous_role_id=role.id).swap()

        assert not authorizer.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(dataset.id)
        )
        assert authorizer.has_resource_role(
            user_id=str(user.id), role_id=str(new_role.id), resource_id=str(dataset.id)
        )
