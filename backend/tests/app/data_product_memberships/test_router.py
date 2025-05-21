from tests.factories import (
    DataProductFactory,
    DataProductMembershipFactory,
    UserFactory,
)
from tests.factories.role import RoleFactory
from tests.factories.role_assignment_global import GlobalRoleAssignmentFactory

from app.core.authz.actions import AuthorizationAction
from app.role_assignments.enums import DecisionStatus
from app.roles.schema import Scope

MEMBERSHIPS_ENDPOINT = "/api/data_product_memberships"


class TestDataProductMembershipsRouter:
    def test_request_data_product_membership(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__REQUEST_DATAPRODUCT_ACCESS],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )
        user = UserFactory()

        response = self.request_data_product_membership(
            client, user.id, data_product.id
        )
        assert response.status_code == 200

    def test_get_pending_actions_no_action(self, client):
        DataProductMembershipFactory(user=UserFactory(external_id="sub"))
        response = client.get(f"{MEMBERSHIPS_ENDPOINT}/actions")
        assert response.json() == []

    def test_get_pending_actions(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductMembershipFactory(user=user).data_product
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__REQUEST_DATAPRODUCT_ACCESS],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )
        self.request_data_product_membership(client, UserFactory().id, data_product.id)
        response = client.get(f"{MEMBERSHIPS_ENDPOINT}/actions")
        assert response.json()[0]["data_product_id"] == str(data_product.id)
        assert response.json()[0]["status"] == "pending"

    @staticmethod
    def request_data_product_membership(client, user_id, data_product_id):
        return client.post(
            f"{MEMBERSHIPS_ENDPOINT}/request?user_id={str(user_id)}"
            f"&data_product_id={str(data_product_id)}"
        )
