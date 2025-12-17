from typing import TYPE_CHECKING

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.auth import DatasetAuthAssignment
from app.authorization.roles.schema import Role, Scope
from app.core.authz import Authorization
from tests.factories import (
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

if TYPE_CHECKING:
    from app.authorization.role_assignments.output_port.schema import RoleAssignment
    from app.data_products.output_ports.model import Dataset
    from app.users.schema import User


class TestAuth:
    def test_add(self, authorizer: Authorization):
        dataset: Dataset = DatasetFactory()
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATASET)
        assert not authorizer.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(dataset.id)
        )
        DatasetRoleAssignmentFactory(
            dataset_id=dataset.id,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        assert authorizer.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(dataset.id)
        )

    def test_remove(self, authorizer: Authorization):
        dataset: Dataset = DatasetFactory()
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATASET)
        assert not authorizer.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(dataset.id)
        )
        assignment: RoleAssignment = DatasetRoleAssignmentFactory(
            dataset_id=dataset.id,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

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
