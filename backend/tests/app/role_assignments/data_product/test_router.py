from fastapi.testclient import TestClient
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from tests.factories.data_product_membership import DataProductMembershipFactory

from app.core.authz.actions import AuthorizationAction
from app.data_products.model import DataProduct
from app.role_assignments.data_product.schema import RoleAssignment
from app.role_assignments.enums import DecisionStatus
from app.roles.schema import Role, Scope
from app.users.schema import User

ENDPOINT = "/api/role_assignments/data_product"
ENDPOINT_DATA_PRODUCT = "/api/data_products"
ENDPOINT_PENDING_ACTIONS = "/api/pending_actions"


class TestDataProductRoleAssignmentsRouter:

    def test_list_assignments(self, client: TestClient):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)
        assignment: RoleAssignment = DataProductRoleAssignmentFactory(
            data_product_id=data_product.id, user_id=user.id, role_id=role.id
        )
        response = client.get(f"{ENDPOINT}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(assignment.id)

    def test_create_assignment(self, client: TestClient):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)

        response = client.post(
            f"{ENDPOINT}",
            json={
                "data_product_id": str(data_product.id),
                "user_id": str(user.id),
                "role_id": str(role.id),
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["data_product"]["id"] == str(data_product.id)
        assert data["user"]["id"] == str(user.id)
        assert data["role"]["id"] == str(role.id)

    def test_delete_assignment(self, client: TestClient):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)
        assignment: RoleAssignment = DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = client.delete(f"{ENDPOINT}/{assignment.id}")
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_decide_assignment(self, client: TestClient):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)
        assignment: RoleAssignment = DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.PENDING,
        )

        response = client.patch(
            f"{ENDPOINT}/{assignment.id}/decide",
            json={"decision": DecisionStatus.APPROVED},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == str(assignment.id)
        assert data["decision"] == DecisionStatus.APPROVED

    def test_decide_assignment_already_decided(self, client: TestClient):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)
        assignment: RoleAssignment = DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.DENIED,
        )

        response = client.patch(
            f"{ENDPOINT}/{assignment.id}/decide",
            json={"decision": DecisionStatus.APPROVED},
        )

        assert response.status_code == 422
        assert "already decided" in response.json()["detail"]

    def test_decide_assignment_idempotency(self, client: TestClient):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)
        assignment: RoleAssignment = DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.DENIED,
        )

        response = client.patch(
            f"{ENDPOINT}/{assignment.id}/decide",
            json={"decision": DecisionStatus.DENIED},
        )
        assert response.status_code == 200

    def test_decide_assignment_no_role(self, client: TestClient):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory()
        assignment: RoleAssignment = DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=None,
        )

        response = client.patch(
            f"{ENDPOINT}/{assignment.id}/decide",
            json={"decision": DecisionStatus.APPROVED},
        )

        assert response.status_code == 422
        assert "does not have a role assignment" in response.json()["detail"]

    def test_modify_assigned_role(self, client: TestClient):
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

        response = client.patch(
            f"{ENDPOINT}/{assignment.id}/role", json={"role_id": str(new_role.id)}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"]["id"] == str(new_role.id)

    def test_delete_data_product_with_role_assignment(self, client: TestClient):
        user = UserFactory(external_id="sub")
        data_product: DataProduct = DataProductMembershipFactory(
            user=user,
        ).data_product
        role: Role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[AuthorizationAction.DATA_PRODUCT__DELETE],
        )
        DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        response = self.delete_data_product(client, data_product.id)
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_pending_actions_no_action(self, client):
        user = UserFactory(external_id="sub")
        data_product: DataProduct = DataProductMembershipFactory(
            user=user,
        ).data_product
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)
        DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )
        response = client.get(f"{ENDPOINT_PENDING_ACTIONS}")
        assert response.json() == []

    def test_request_data_product_role_assignment_with_accept_permission(self, client):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory(external_id="sub")
        role: Role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[AuthorizationAction.DATA_PRODUCT__APPROVE_USER_REQUEST],
        )
        DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )
        user_requester: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)

        response = client.post(
            f"{ENDPOINT}",
            json={
                "data_product_id": str(data_product.id),
                "user_id": str(user_requester.id),
                "role_id": str(role.id),
            },
        )
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT_PENDING_ACTIONS}")
        assert response.status_code == 200
        assert len(response.json()) == 0
        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert (
            data[0].get("decision") != DecisionStatus.PENDING
            and data[1].get("decision") != DecisionStatus.PENDING
        )

    def test_request_data_product_role_assignment_without_accept_permission(
        self, client
    ):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory(external_id="sub")
        role: Role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[AuthorizationAction.DATA_PRODUCT__CREATE_USER],
        )
        DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )
        user_requester: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)

        response = client.post(
            f"{ENDPOINT}",
            json={
                "data_product_id": str(data_product.id),
                "user_id": str(user_requester.id),
                "role_id": str(role.id),
            },
        )
        assert response.status_code == 200
        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert (
            data[0].get("decision") == DecisionStatus.PENDING
            or data[1].get("decision") == DecisionStatus.PENDING
        )

    @staticmethod
    def delete_data_product(client, data_product_id):
        return client.delete(f"{ENDPOINT_DATA_PRODUCT}/{data_product_id}")
