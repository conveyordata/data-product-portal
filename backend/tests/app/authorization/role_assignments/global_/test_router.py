from typing import TYPE_CHECKING

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Role, Scope
from app.core.authz.actions import AuthorizationAction
from app.identities.type import IdentityType
from app.settings import settings
from tests.factories import (
    GlobalRoleAssignmentFactory,
    GroupFactory,
    MachineUserFactory,
    OutputPortFactory,
    RoleFactory,
    UserFactory,
)

if TYPE_CHECKING:
    from app.authorization.role_assignments.global_.schema import GlobalRoleAssignment
    from app.users.schema import User

ENDPOINT = "/api/v2/authz/role_assignments/global"
IDENTITY_CASES = [
    pytest.param(UserFactory, IdentityType.USER, "email", id="user"),
    pytest.param(GroupFactory, IdentityType.GROUP, "display_name", id="group"),
    pytest.param(
        MachineUserFactory, IdentityType.MACHINE_USER, "display_name", id="machine_user"
    ),
]


class TestGlobalRoleAssignmentsRouter:
    @pytest.mark.parametrize(
        ("identity_factory", "identity_type", "detail_field"),
        IDENTITY_CASES,
    )
    def test_list_assignments__identity(
        self,
        client: TestClient,
        identity_factory,
        identity_type: IdentityType,
        detail_field: str,
    ):
        identity = identity_factory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        assignment: GlobalRoleAssignment = GlobalRoleAssignmentFactory(
            identity_id=identity.id,
            role_id=role.id,
        )

        response = client.get(
            ENDPOINT,
            params={"identity_id": str(identity.id)},
        )

        assert response.status_code == status.HTTP_200_OK
        assignments = response.json()["role_assignments"]
        assert len(assignments) == 1

        response_assignment = assignments[0]
        response_identity = response_assignment["identity"]

        assert response_assignment["id"] == str(assignment.id)
        assert response_identity["id"] == str(identity.id)
        assert response_identity["type"] == identity_type.value
        assert response_identity["external_id"] == identity.external_id
        assert response_identity[detail_field] == str(getattr(identity, detail_field))
        assert response_assignment["role"]["id"] == str(role.id)

    @pytest.mark.parametrize(
        ("identity_factory", "identity_type", "detail_field"),
        IDENTITY_CASES,
    )
    def test_create_assignment__identity(
        self,
        client: TestClient,
        identity_factory,
        identity_type: IdentityType,
        detail_field: str,
    ):
        me = UserFactory(external_id=settings.DEFAULT_USERNAME)
        authorization_role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_USER],
        )
        GlobalRoleAssignmentFactory(
            identity_id=me.id,
            role_id=authorization_role.id,
        )
        identity = identity_factory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)

        response = client.post(
            ENDPOINT,
            json={
                "identity_id": str(identity.id),
                "role_id": str(role.id),
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assignment = response.json()
        response_identity = assignment["identity"]

        assert response_identity["id"] == str(identity.id)
        assert response_identity["type"] == identity_type.value
        assert response_identity["external_id"] == identity.external_id
        assert response_identity[detail_field] == str(getattr(identity, detail_field))
        assert assignment["role"]["id"] == str(role.id)

    def test_become_admin(self, client: TestClient):
        UserFactory(external_id=settings.DEFAULT_USERNAME, can_become_admin=True)
        ds = OutputPortFactory()

        delete = client.delete(
            f"/api/v2/data_products/{ds.data_product_id}/output_ports/{ds.id}"
        )
        assert delete.status_code == status.HTTP_403_FORBIDDEN

        response = client.post(
            f"{ENDPOINT}/become_admin",
            json={"expiry": "2024-12-31T23:59:59Z"},
        )
        assert response.status_code == status.HTTP_200_OK

        # User became admin, can delete datasets now
        delete = client.delete(
            f"/api/v2/data_products/{ds.data_product_id}/output_ports/{ds.id}"
        )
        assert delete.status_code == status.HTTP_200_OK

    def test_become_admin_not_allowed(self, client: TestClient):
        UserFactory(external_id=settings.DEFAULT_USERNAME, can_become_admin=False)

        response = client.post(
            f"{ENDPOINT}/become_admin",
            json={"expiry": "2024-12-31T23:59:59Z"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_revoke_admin(self, client: TestClient):
        UserFactory(external_id=settings.DEFAULT_USERNAME, can_become_admin=True)

        response = client.post(
            f"{ENDPOINT}/revoke_admin",
        )
        assert response.status_code == status.HTTP_200_OK
        response = client.post(
            f"{ENDPOINT}/become_admin",
            json={"expiry": "2024-12-31T23:59:59Z"},
        )
        assert response.status_code == status.HTTP_200_OK

        response = client.post(
            f"{ENDPOINT}/revoke_admin",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_create_assignment_admin(self, client: TestClient):
        me = UserFactory(external_id=settings.DEFAULT_USERNAME)
        RoleFactory.admin()
        authz_role = RoleFactory(
            scope=Scope.GLOBAL, permissions=[AuthorizationAction.GLOBAL__CREATE_USER]
        )
        GlobalRoleAssignmentFactory(identity_id=me.id, role_id=authz_role.id)
        user: User = UserFactory()

        response = client.post(
            f"{ENDPOINT}",
            json={
                "identity_id": str(user.id),
                "role_id": "admin",
            },
        )
        # Create admin assignment is no longer allowed
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_assignment(self, client: TestClient):
        me = UserFactory(external_id=settings.DEFAULT_USERNAME)
        authz_role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__DELETE_USER],
        )
        GlobalRoleAssignmentFactory(identity_id=me.id, role_id=authz_role.id)
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        assignment: GlobalRoleAssignment = GlobalRoleAssignmentFactory(
            identity_id=user.id,
            role_id=role.id,
        )

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["role_assignments"]) == 2

        response = client.delete(f"{ENDPOINT}/{assignment.id}")
        assert response.status_code == status.HTTP_200_OK

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["role_assignments"]) == 1

    def test_decide_assignment(self, client: TestClient):
        me = UserFactory(external_id=settings.DEFAULT_USERNAME)
        authz_role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_USER],
        )
        GlobalRoleAssignmentFactory(identity_id=me.id, role_id=authz_role.id)
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        assignment: GlobalRoleAssignment = GlobalRoleAssignmentFactory(
            identity_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.PENDING,
        )

        response = client.post(
            f"{ENDPOINT}/{assignment.id}/decide",
            json={"decision": DecisionStatus.APPROVED},
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == str(assignment.id)
        assert data["decision"] == DecisionStatus.APPROVED

    def test_decide_assignment_already_decided(self, client: TestClient):
        me = UserFactory(external_id=settings.DEFAULT_USERNAME)
        authz_role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_USER],
        )
        GlobalRoleAssignmentFactory(identity_id=me.id, role_id=authz_role.id)
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        assignment: GlobalRoleAssignment = GlobalRoleAssignmentFactory(
            identity_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.DENIED,
        )

        response = client.post(
            f"{ENDPOINT}/{assignment.id}/decide",
            json={"decision": DecisionStatus.APPROVED},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "already decided" in response.json()["detail"]

    def test_decide_assignment_idempotency(self, client: TestClient):
        me = UserFactory(external_id=settings.DEFAULT_USERNAME)
        authz_role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_USER],
        )
        GlobalRoleAssignmentFactory(identity_id=me.id, role_id=authz_role.id)
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        assignment: GlobalRoleAssignment = GlobalRoleAssignmentFactory(
            identity_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.DENIED,
        )

        response = client.post(
            f"{ENDPOINT}/{assignment.id}/decide",
            json={"decision": DecisionStatus.DENIED},
        )
        assert response.status_code == status.HTTP_200_OK

    def test_modify_assigned_role(self, client: TestClient):
        me = UserFactory(external_id=settings.DEFAULT_USERNAME)
        authz_role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_USER],
        )
        GlobalRoleAssignmentFactory(identity_id=me.id, role_id=authz_role.id)
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        new_role: Role = RoleFactory(scope=Scope.GLOBAL)

        assignment: GlobalRoleAssignment = GlobalRoleAssignmentFactory(
            identity_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        response = client.put(
            f"{ENDPOINT}/{assignment.id}/role", json={"role_id": str(new_role.id)}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"]["id"] == str(new_role.id)

    def test_modify_assigned_role_from_admin(self, client: TestClient):
        me = UserFactory(external_id=settings.DEFAULT_USERNAME)
        authz_role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_USER],
        )
        GlobalRoleAssignmentFactory(identity_id=me.id, role_id=authz_role.id)
        user1, user2 = UserFactory.create_batch(2)
        admin: Role = RoleFactory.admin()
        role: Role = RoleFactory(scope=Scope.GLOBAL)

        assignment: GlobalRoleAssignment = GlobalRoleAssignmentFactory(
            identity_id=user1.id,
            role_id=admin.id,
        )
        GlobalRoleAssignmentFactory(identity_id=user2.id, role_id=admin.id)

        response = client.put(
            f"{ENDPOINT}/{assignment.id}/role", json={"role_id": str(role.id)}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"]["id"] == str(role.id)

    def test_modify_assigned_role_to_admin(self, client: TestClient):
        me = UserFactory(external_id=settings.DEFAULT_USERNAME)
        authz_role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[AuthorizationAction.GLOBAL__CREATE_USER],
        )
        GlobalRoleAssignmentFactory(identity_id=me.id, role_id=authz_role.id)
        user: User = UserFactory()
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        admin: Role = RoleFactory.admin()

        assignment: GlobalRoleAssignment = GlobalRoleAssignmentFactory(
            identity_id=user.id,
            role_id=role.id,
        )

        response = client.put(
            f"{ENDPOINT}/{assignment.id}/role", json={"role_id": "admin"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"]["id"] == str(admin.id)

    def test_delete_last_admin_assignment(self, client: TestClient):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.GLOBAL, permissions=[AuthorizationAction.GLOBAL__DELETE_USER]
        )
        GlobalRoleAssignmentFactory(
            identity_id=user.id,
            role_id=role.id,
        )

        user_1, user_2 = UserFactory.create_batch(2)
        admin: Role = RoleFactory.admin()
        assignment_1 = GlobalRoleAssignmentFactory(
            identity_id=user_1.id,
            role_id=admin.id,
        )
        assignment_2 = GlobalRoleAssignmentFactory(
            identity_id=user_2.id,
            role_id=admin.id,
        )

        response = client.delete(f"{ENDPOINT}/{assignment_1.id}")
        assert response.status_code == status.HTTP_200_OK

        response = client.delete(f"{ENDPOINT}/{assignment_2.id}")
        assert response.status_code == status.HTTP_200_OK  # No longer an issue
