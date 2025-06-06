import pytest
from fastapi import status
from fastapi.testclient import TestClient
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from tests.factories.role_assignment_global import GlobalRoleAssignmentFactory

from app.core.authz import Action
from app.data_products.model import DataProduct
from app.role_assignments.data_product.schema import RoleAssignment
from app.role_assignments.enums import DecisionStatus
from app.roles.schema import Prototype, Role, Scope
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

    @pytest.mark.parametrize(
        "permissions",
        [
            [
                Action.DATA_PRODUCT__CREATE_USER,
            ],
            [
                Action.DATA_PRODUCT__CREATE_USER,
                Action.DATA_PRODUCT__APPROVE_USER_REQUEST,
            ],
        ],
    )
    def test_create_assignment(self, permissions: list[Action], client: TestClient):
        data_product: DataProduct = DataProductFactory()
        me = UserFactory(external_id="sub")
        authz_role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=permissions,
        )
        DataProductRoleAssignmentFactory(
            user_id=me.id, role_id=authz_role.id, data_product_id=data_product.id
        )
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)

        response = client.post(
            f"{ENDPOINT}/{str(data_product.id)}",
            json={
                "user_id": str(user.id),
                "role_id": str(role.id),
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["data_product"]["id"] == str(data_product.id)
        assert data["user"]["id"] == str(user.id)
        assert data["role"]["id"] == str(role.id)

    def test_request_assignment(self, client: TestClient):
        data_product: DataProduct = DataProductFactory()
        me = UserFactory(external_id="sub")
        authz_role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__REQUEST_DATAPRODUCT_ACCESS],
        )
        GlobalRoleAssignmentFactory(user_id=me.id, role_id=authz_role.id)
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)

        response = client.post(
            f"{ENDPOINT}/request/{str(data_product.id)}",
            json={
                "user_id": str(user.id),
                "role_id": str(role.id),
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["data_product"]["id"] == str(data_product.id)
        assert data["user"]["id"] == str(user.id)
        assert data["role"]["id"] == str(role.id)

    def test_request_assignment_no_right(self, client: TestClient):
        data_product: DataProduct = DataProductFactory()
        UserFactory(external_id="sub")

        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)

        response = client.post(
            f"{ENDPOINT}/request/{str(data_product.id)}",
            json={
                "user_id": str(user.id),
                "role_id": str(role.id),
            },
        )
        assert response.status_code == 403

    def test_delete_assignment(self, client: TestClient):
        data_product: DataProduct = DataProductFactory()
        me = UserFactory(external_id="sub")
        authz_role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATA_PRODUCT__DELETE_USER],
        )
        DataProductRoleAssignmentFactory(
            user_id=me.id, role_id=authz_role.id, data_product_id=data_product.id
        )
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)
        assignment: RoleAssignment = DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=role.id,
        )

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()) == 2

        response = client.delete(f"{ENDPOINT}/{assignment.id}")
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_delete_last_owner_assignment(self, client: TestClient):
        data_product: DataProduct = DataProductFactory()
        user = UserFactory(external_id="sub")
        authz_role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATA_PRODUCT__DELETE_USER],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=authz_role.id, data_product_id=data_product.id
        )

        user_1, user_2 = UserFactory.create_batch(2)
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT, prototype=Prototype.OWNER)
        assignment_1 = DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user_1.id,
            role_id=role.id,
        )
        assignment_2 = DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user_2.id,
            role_id=role.id,
        )

        response = client.delete(f"{ENDPOINT}/{assignment_1.id}")
        assert response.status_code == status.HTTP_200_OK

        response = client.delete(f"{ENDPOINT}/{assignment_2.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_decide_assignment(self, client: TestClient):
        data_product: DataProduct = DataProductFactory()
        me = UserFactory(external_id="sub")
        authz_role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATA_PRODUCT__APPROVE_USER_REQUEST],
        )
        DataProductRoleAssignmentFactory(
            user_id=me.id, role_id=authz_role.id, data_product_id=data_product.id
        )
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
        me = UserFactory(external_id="sub")
        authz_role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATA_PRODUCT__APPROVE_USER_REQUEST],
        )
        DataProductRoleAssignmentFactory(
            user_id=me.id, role_id=authz_role.id, data_product_id=data_product.id
        )
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
        me = UserFactory(external_id="sub")
        authz_role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATA_PRODUCT__APPROVE_USER_REQUEST],
        )
        DataProductRoleAssignmentFactory(
            user_id=me.id, role_id=authz_role.id, data_product_id=data_product.id
        )
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
        me = UserFactory(external_id="sub")
        authz_role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATA_PRODUCT__APPROVE_USER_REQUEST],
        )
        DataProductRoleAssignmentFactory(
            user_id=me.id, role_id=authz_role.id, data_product_id=data_product.id
        )
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
        me = UserFactory(external_id="sub")
        authz_role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_USER],
        )
        DataProductRoleAssignmentFactory(
            user_id=me.id, role_id=authz_role.id, data_product_id=data_product.id
        )
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
            f"{ENDPOINT}/{assignment.id}", json={"role_id": str(new_role.id)}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"]["id"] == str(new_role.id)

    def test_modify_last_owner(self, client: TestClient):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory()
        owner: Role = RoleFactory(scope=Scope.DATA_PRODUCT, prototype=Prototype.OWNER)
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT, prototype=Prototype.CUSTOM)

        assignment: RoleAssignment = DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=owner.id,
            decision=DecisionStatus.APPROVED,
        )

        response = client.patch(
            f"{ENDPOINT}/{assignment.id}", json={"role_id": str(role.id)}
        )
        assert response.status_code == 403

    def test_delete_data_product_with_role_assignment(self, client: TestClient):
        user = UserFactory(external_id="sub")
        data_product: DataProduct = DataProductFactory()
        role: Role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__DELETE],
        )
        DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=role.id,
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

    def test_get_pending_actions_no_action(self, client: TestClient):
        user = UserFactory(external_id="sub")
        data_product: DataProduct = DataProductFactory()
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT)
        DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=role.id,
        )
        response = client.get(f"{ENDPOINT_PENDING_ACTIONS}")
        assert response.json() == []

    def test_request_data_product_role_assignment_with_accept_permission(
        self, client: TestClient
    ):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory(external_id="sub")
        role1: Role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[
                Action.DATA_PRODUCT__CREATE_USER,
                Action.DATA_PRODUCT__APPROVE_USER_REQUEST,
            ],
        )
        DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=role1.id,
        )
        user_requester: User = UserFactory()
        role2: Role = RoleFactory(scope=Scope.DATA_PRODUCT)

        response = client.post(
            f"{ENDPOINT}/{str(data_product.id)}",
            json={
                "user_id": str(user_requester.id),
                "role_id": str(role2.id),
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
        self, client: TestClient
    ):
        data_product: DataProduct = DataProductFactory()
        user: User = UserFactory(external_id="sub")
        role1: Role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__CREATE_USER],
        )
        DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=role1.id,
        )
        user_requester: User = UserFactory()
        role2: Role = RoleFactory(scope=Scope.DATA_PRODUCT)

        response = client.post(
            f"{ENDPOINT}/{str(data_product.id)}",
            json={
                "user_id": str(user_requester.id),
                "role_id": str(role2.id),
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
    def delete_data_product(client: TestClient, data_product_id: str):
        return client.delete(f"{ENDPOINT_DATA_PRODUCT}/{data_product_id}")
