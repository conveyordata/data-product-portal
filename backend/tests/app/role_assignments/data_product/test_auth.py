from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

from app.core.authz import Authorization
from app.data_products.model import DataProduct
from app.role_assignments.data_product.auth import DataProductAuthAssignment
from app.role_assignments.data_product.schema import RoleAssignment
from app.role_assignments.enums import DecisionStatus
from app.roles.schema import Role, Scope
from app.users.schema import User


class TestAuth:
    def test_add(self, authorizer: Authorization):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)

        assignment: RoleAssignment = DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        assert not authorizer.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(data_product.id)
        )
        DataProductAuthAssignment(assignment).add()
        assert authorizer.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(data_product.id)
        )

    def test_remove(self, authorizer: Authorization):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)

        assignment: RoleAssignment = DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        assert not authorizer.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(data_product.id)
        )
        DataProductAuthAssignment(assignment).add()
        assert authorizer.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(data_product.id)
        )
        DataProductAuthAssignment(assignment).remove()
        assert not authorizer.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(data_product.id)
        )

    def test_swap(self, authorizer: Authorization):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)
        new_role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)

        assignment: RoleAssignment = DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        DataProductAuthAssignment(assignment).add()
        assert authorizer.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(data_product.id)
        )

        assignment.role_id = new_role.id
        DataProductAuthAssignment(assignment, previous_role_id=role.id).swap()

        assert not authorizer.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(data_product.id)
        )
        assert authorizer.has_resource_role(
            user_id=str(user.id),
            role_id=str(new_role.id),
            resource_id=str(data_product.id),
        )
