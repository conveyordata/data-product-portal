from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

from app.core.authz import Action
from app.role_assignments.data_product.service import RoleAssignmentService
from app.roles.schema import Scope


class TestDataProductRoleAssignmentsService:

    def test_user_has_permission(self, session):
        service = RoleAssignmentService(db=session)
        data_product = DataProductFactory()
        action = Action.DATA_PRODUCT__REQUEST_DATASET_ACCESS

        authorized_users = service.users_with_authz_action(
            data_product_id=data_product.id,
            action=action,
        )
        assert len(authorized_users) == 0

        user = UserFactory()
        role = RoleFactory(scope=Scope.DATA_PRODUCT, permissions=[action])
        DataProductRoleAssignmentFactory(
            data_product_id=data_product.id, user_id=user.id, role_id=role.id
        )

        authorized_users = service.users_with_authz_action(
            data_product_id=data_product.id,
            action=action,
        )
        assert user.id in (auth_user.id for auth_user in authorized_users)
