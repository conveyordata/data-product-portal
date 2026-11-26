from typing import TYPE_CHECKING

import pytest

from app.authorization.role_assignments.data_product.auth import (
    DataProductAuthAssignment,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Role, Scope
from app.core.authz import CasbinPolicies
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

if TYPE_CHECKING:
    from app.authorization.role_assignments.data_product.schema import (
        DataProductRoleAssignment,
    )
    from app.data_products.model import DataProduct
    from app.users.schema import User


class TestAuth:
    def test_add(self, policies: CasbinPolicies):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)

        assert not policies.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(data_product.id)
        )

        DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            identity_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        assert policies.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(data_product.id)
        )

    def test_remove(self, policies: CasbinPolicies):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)

        assert not policies.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(data_product.id)
        )

        assignment: DataProductRoleAssignment = DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            identity_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        assert policies.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(data_product.id)
        )
        DataProductAuthAssignment(assignment).remove()
        assert not policies.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(data_product.id)
        )

    @pytest.mark.seeds_casbin
    def test_swap(self, policies: CasbinPolicies):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)
        new_role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)

        assignment: DataProductRoleAssignment = DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            identity_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        DataProductAuthAssignment(assignment).add()
        assert policies.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(data_product.id)
        )

        assignment.role_id = new_role.id
        DataProductAuthAssignment(assignment, previous_role_id=role.id).swap()

        assert not policies.has_resource_role(
            user_id=str(user.id), role_id=str(role.id), resource_id=str(data_product.id)
        )
        assert policies.has_resource_role(
            user_id=str(user.id),
            role_id=str(new_role.id),
            resource_id=str(data_product.id),
        )
