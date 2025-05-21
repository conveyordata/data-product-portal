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

        json = {
            "data_product_id": str(data_product.id),
            "user_id": str(user.id),
            "role_id": str(role.id),
        }
        response = self.create_data_product_role_assignment(client, json)
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

        response = self.delete_data_product_role_assignment(client, assignment.id)
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

        response = self.approve_data_product_role_assignment(client, assignment.id)
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

        response = self.approve_data_product_role_assignment(client, assignment.id)

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

        response = self.deny_data_product_role_assignment(client, assignment.id)

        assert response.status_code == 200

    def test_decide_assignment_no_role(self, client: TestClient):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory()
        assignment: RoleAssignment = DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=None,
        )

        response = self.approve_data_product_role_assignment(client, assignment.id)

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

        json = {"role_id": str(new_role.id)}
        response = self.modify_data_product_role_assignment(client, assignment.id, json)
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

    def test_data_product_membership_history(self, client):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)

        json = {
            "data_product_id": str(data_product.id),
            "user_id": str(user.id),
            "role_id": str(role.id),
        }
        assignment_requested = self.create_data_product_role_assignment(client, json)
        assignment_id = assignment_requested.json().get("id")
        assert assignment_id is not None
        response = self.get_data_product_history(client, data_product.id)
        assert len(response.json()) == 1

        response = self.approve_data_product_role_assignment(client, assignment_id)
        assert response.status_code == 200
        response = self.get_data_product_history(client, data_product.id)
        assert len(response.json()) == 2

        new_role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)
        json = {"role_id": str(new_role.id)}
        response = self.modify_data_product_role_assignment(client, assignment_id, json)
        assert response.status_code == 200
        response = self.get_data_product_history(client, data_product.id)
        assert len(response.json()) == 3

        response = self.delete_data_product_role_assignment(client, assignment_id)
        assert response.status_code == 200
        response = self.get_data_product_history(client, data_product.id)
        assert len(response.json()) == 4

    @staticmethod
    def delete_data_product(client, data_product_id):
        return client.delete(f"{ENDPOINT_DATA_PRODUCT}/{data_product_id}")

    @staticmethod
    def create_data_product_role_assignment(client, json):
        return client.post(
            f"{ENDPOINT}",
            json=json,
        )

    @staticmethod
    def delete_data_product_role_assignment(client, assignment_id):
        return client.delete(f"{ENDPOINT}/{assignment_id}")

    @staticmethod
    def approve_data_product_role_assignment(client, assignment_id):
        return client.patch(
            f"{ENDPOINT}/{assignment_id}/decide",
            json={"decision": DecisionStatus.APPROVED},
        )

    @staticmethod
    def deny_data_product_role_assignment(client, assignment_id):
        return client.patch(
            f"{ENDPOINT}/{assignment_id}/decide",
            json={"decision": DecisionStatus.DENIED},
        )

    @staticmethod
    def modify_data_product_role_assignment(client, assignment_id, json):
        return client.patch(f"{ENDPOINT}/{assignment_id}/role", json=json)

    @staticmethod
    def get_data_product_history(client, data_product_id):
        return client.get(f"{ENDPOINT_DATA_PRODUCT}/{data_product_id}/history")
