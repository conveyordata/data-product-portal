from fastapi import status
from fastapi.testclient import TestClient
from tests.factories import GlobalRoleAssignmentFactory, RoleFactory, UserFactory

from app.core.authz.actions import AuthorizationAction
from app.role_assignments.enums import DecisionStatus
from app.role_assignments.global_.schema import RoleAssignment
from app.roles.schema import Role, Scope
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

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(assignment.id)

    def test_create_assignment(self, client: TestClient):
        me = UserFactory(external_id="sub")
        authz_role = RoleFactory(
            scope=Scope.GLOBAL, permissions=[AuthorizationAction.GLOBAL__CREATE_USER]
        )
        GlobalRoleAssignmentFactory(user_id=me.id, role_id=authz_role.id)
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)

        response = client.post(
            f"{ENDPOINT}",
            json={
                "user_id": str(user.id),
                "role_id": str(role.id),
            },
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["user"]["id"] == str(user.id)
        assert data["role"]["id"] == str(role.id)

    def test_create_assignment_admin(self, client: TestClient):
        me = UserFactory(external_id="sub")
        authz_role = RoleFactory(
            scope=Scope.GLOBAL, permissions=[AuthorizationAction.GLOBAL__CREATE_USER]
        )
        GlobalRoleAssignmentFactory(user_id=me.id, role_id=authz_role.id)
        user: User = UserFactory()
        admin: Role = RoleFactory.admin()

        response = client.post(
            f"{ENDPOINT}",
            json={
                "user_id": str(user.id),
                "role_id": "admin",
            },
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["user"]["id"] == str(user.id)
        assert data["role"]["id"] == str(admin.id)

    def test_delete_assignment(self, client: TestClient):
        me = UserFactory(external_id="sub")
        authz_role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__DELETE_USER],
        )
        GlobalRoleAssignmentFactory(user_id=me.id, role_id=authz_role.id)
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        assignment: RoleAssignment = GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2

        response = client.delete(f"{ENDPOINT}/{assignment.id}")
        assert response.status_code == status.HTTP_200_OK

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

    def test_decide_assignment(self, client: TestClient):
        me = UserFactory(external_id="sub")
        authz_role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_USER],
        )
        GlobalRoleAssignmentFactory(user_id=me.id, role_id=authz_role.id)
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
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == str(assignment.id)
        assert data["decision"] == DecisionStatus.APPROVED

    def test_decide_assignment_already_decided(self, client: TestClient):
        me = UserFactory(external_id="sub")
        authz_role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_USER],
        )
        GlobalRoleAssignmentFactory(user_id=me.id, role_id=authz_role.id)
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

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "already decided" in response.json()["detail"]

    def test_decide_assignment_idempotency(self, client: TestClient):
        me = UserFactory(external_id="sub")
        authz_role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_USER],
        )
        GlobalRoleAssignmentFactory(user_id=me.id, role_id=authz_role.id)
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
        assert response.status_code == status.HTTP_200_OK

    def test_modify_assigned_role(self, client: TestClient):
        me = UserFactory(external_id="sub")
        authz_role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_USER],
        )
        GlobalRoleAssignmentFactory(user_id=me.id, role_id=authz_role.id)
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
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"]["id"] == str(new_role.id)

    def test_modify_assigned_role_from_admin(self, client: TestClient):
        me = UserFactory(external_id="sub")
        authz_role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_USER],
        )
        GlobalRoleAssignmentFactory(user_id=me.id, role_id=authz_role.id)
        user1, user2 = UserFactory.create_batch(2)
        admin: Role = RoleFactory.admin()
        role: Role = RoleFactory(scope=Scope.GLOBAL)

        assignment: RoleAssignment = GlobalRoleAssignmentFactory(
            user_id=user1.id,
            role_id=admin.id,
        )
        GlobalRoleAssignmentFactory(user_id=user2.id, role_id=admin.id)

        response = client.patch(
            f"{ENDPOINT}/{assignment.id}/role", json={"role_id": str(role.id)}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"]["id"] == str(role.id)

    def test_modify_assigned_role_to_admin(self, client: TestClient):
        me = UserFactory(external_id="sub")
        authz_role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_USER],
        )
        GlobalRoleAssignmentFactory(user_id=me.id, role_id=authz_role.id)
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        admin: Role = RoleFactory.admin()

        assignment: RoleAssignment = GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )

        response = client.patch(
            f"{ENDPOINT}/{assignment.id}/role", json={"role_id": "admin"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"]["id"] == str(admin.id)

    def test_delete_last_admin_assignment(self, client: TestClient):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.GLOBAL, permissions=[AuthorizationAction.GLOBAL__DELETE_USER]
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )

        user_1, user_2 = UserFactory.create_batch(2)
        admin: Role = RoleFactory.admin()
        assignment_1 = GlobalRoleAssignmentFactory(
            user_id=user_1.id,
            role_id=admin.id,
        )
        assignment_2 = GlobalRoleAssignmentFactory(
            user_id=user_2.id,
            role_id=admin.id,
        )

        response = client.delete(f"{ENDPOINT}/{assignment_1.id}")
        assert response.status_code == status.HTTP_200_OK

        response = client.delete(f"{ENDPOINT}/{assignment_2.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN
