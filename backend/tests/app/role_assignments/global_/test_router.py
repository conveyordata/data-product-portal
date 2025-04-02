from fastapi.testclient import TestClient
from tests.factories import (
    GlobalRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

from app.role_assignments.enums import DecisionStatus
from app.role_assignments.global_.schema import RoleAssignment
from app.roles.schema import Role, Scope
from app.roles.service import ADMIN_UUID
from app.users.schema import User

ENDPOINT = "/api/role_assignments/global"


class TestGlobalRoleAssignmentsRouter:

    def test_list_assignments(self, client: TestClient):
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        assignment: RoleAssignment = GlobalRoleAssignmentFactory(
            user_id=user.id, role_id=role.id
        )
        response = client.get(f"{ENDPOINT}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(assignment.id)

    def test_create_assignment(self, client: TestClient):
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)

        response = client.post(
            f"{ENDPOINT}",
            json={
                "user_id": str(user.id),
                "role_id": str(role.id),
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["user"]["id"] == str(user.id)
        assert data["role"]["id"] == str(role.id)

    def test_create_assignment_admin(self, client: TestClient):
        user: User = UserFactory()
        _: Role = RoleFactory(scope=Scope.GLOBAL, id=ADMIN_UUID)

        response = client.post(
            f"{ENDPOINT}",
            json={
                "user_id": str(user.id),
                "role_id": "admin",
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["user"]["id"] == str(user.id)
        assert data["role"]["id"] == str(ADMIN_UUID)

    def test_delete_assignment(self, client: TestClient):
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        assignment: RoleAssignment = GlobalRoleAssignmentFactory(
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
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        assignment: RoleAssignment = GlobalRoleAssignmentFactory(
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
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        assignment: RoleAssignment = GlobalRoleAssignmentFactory(
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
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        assignment: RoleAssignment = GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.DENIED,
        )

        response = client.patch(
            f"{ENDPOINT}/{assignment.id}/decide",
            json={"decision": DecisionStatus.DENIED},
        )
        assert response.status_code == 200

    def test_modify_assigned_role(self, client: TestClient):
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        new_role: Role = RoleFactory(scope=Scope.GLOBAL)

        assignment: RoleAssignment = GlobalRoleAssignmentFactory(
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

    def test_modify_assigned_role_from_admin(self, client: TestClient):
        user: User = UserFactory()
        admin: Role = RoleFactory(scope=Scope.GLOBAL, id=ADMIN_UUID)
        role: Role = RoleFactory(scope=Scope.GLOBAL)

        assignment: RoleAssignment = GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=admin.id,
            decision=DecisionStatus.APPROVED,
        )

        response = client.patch(
            f"{ENDPOINT}/{assignment.id}/role", json={"role_id": str(role.id)}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"]["id"] == str(role.id)

    def test_modify_assigned_role_to_admin(self, client: TestClient):
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        admin: Role = RoleFactory(scope=Scope.GLOBAL, id=ADMIN_UUID)

        assignment: RoleAssignment = GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        response = client.patch(
            f"{ENDPOINT}/{assignment.id}/role", json={"role_id": "admin"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"]["id"] == str(admin.id)
