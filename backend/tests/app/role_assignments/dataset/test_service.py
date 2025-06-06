from tests.factories import (
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

from app.core.authz import Action
from app.role_assignments.dataset.service import RoleAssignmentService
from app.roles.schema import Scope


class TestDatasetRoleAssignmentsService:

    def test_user_has_permission(self, session):
        service = RoleAssignmentService(db=session)
        dataset = DatasetFactory()
        action = Action.DATASET__READ_INTEGRATIONS

        authorized_users = service.users_with_authz_action(
            dataset_id=dataset.id,
            action=action,
        )
        assert len(authorized_users) == 0

        user = UserFactory()
        role = RoleFactory(scope=Scope.DATASET, permissions=[action])
        DatasetRoleAssignmentFactory(
            dataset_id=dataset.id, user_id=user.id, role_id=role.id
        )

        authorized_users = service.users_with_authz_action(
            dataset_id=dataset.id,
            action=action,
        )
        assert user.id in (auth_user.id for auth_user in authorized_users)
