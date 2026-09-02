import pytest
from fastapi.testclient import TestClient

from app.authorization.roles import ADMIN_UUID
from app.authorization.roles.schema import Role, Scope
from app.core.authz.actions import AuthorizationAction
from tests.factories import RoleFactory

ENDPOINT = "/api/v2/authz/roles"


class TestRolesRouter:
    test_role = {
        "name": "test",
        "scope": "dataset",
        "description": "test description",
        "permissions": [AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
    }

    def test_get_roles(self, client: TestClient):
        response = client.get(f"{ENDPOINT}/global")

        assert response.status_code == 200
        data = response.json()
        assert len(data["roles"]) == 2  # We return the 2 global roles

    @pytest.mark.usefixtures("admin")
    def test_create_role(self, client: TestClient):
        response = client.post(
            ENDPOINT,
            json={
                "name": self.test_role["name"],
                "scope": self.test_role["scope"],
                "description": self.test_role["description"],
                "permissions": self.test_role["permissions"],
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == self.test_role["name"]
        assert data["scope"] == self.test_role["scope"]
        assert data["description"] == self.test_role["description"]
        assert len(data["permissions"]) == 2
        assert AuthorizationAction.HIDDEN__OUTPUT_PORT__READ in data["permissions"]
        for permission in self.test_role["permissions"]:
            assert permission in data["permissions"]

    @pytest.mark.usefixtures("admin")
    def test_create_data_product_role_adds_read_permission(self, client: TestClient):
        response = client.post(
            ENDPOINT,
            json={
                "name": "data product role",
                "scope": Scope.DATA_PRODUCT,
                "description": "data product role description",
                "permissions": [
                    int(AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES)
                ],
            },
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["scope"] == Scope.DATA_PRODUCT
        assert AuthorizationAction.HIDDEN__DATA_PRODUCT__READ in data["permissions"]
        assert data["permissions"] == sorted(
            [
                int(AuthorizationAction.HIDDEN__DATA_PRODUCT__READ),
                int(AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES),
            ]
        )

    @pytest.mark.usefixtures("admin")
    def test_update_role_old(self, client: TestClient):
        role: Role = RoleFactory()
        response = client.put(
            f"{ENDPOINT}/{role.id}",
            json={
                "permissions": [101, 102],
                "description": "updated_description",
            },
        )
        assert response.status_code == 200, response.text

    @pytest.mark.usefixtures("admin")
    def test_update_data_product_role_adds_read_permission(self, client: TestClient):
        role: Role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[int(AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES)],
        )
        response = client.put(
            f"{ENDPOINT}/{role.id}",
            json={
                "permissions": [
                    int(AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES),
                    int(AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS),
                ],
                "description": "updated_description",
            },
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["id"] == str(role.id)
        assert data["scope"] == role.scope
        assert data["description"] == "updated_description"
        assert AuthorizationAction.HIDDEN__DATA_PRODUCT__READ in data["permissions"]
        assert data["permissions"] == sorted(
            [
                int(AuthorizationAction.HIDDEN__DATA_PRODUCT__READ),
                int(AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES),
                int(AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS),
            ]
        )

    @pytest.mark.usefixtures("admin")
    def test_update_role(self, client: TestClient):
        role: Role = RoleFactory(scope=Scope.GLOBAL)
        response = client.put(
            f"{ENDPOINT}/{role.id}",
            json={
                "permissions": [101, 102],
                "description": "updated_description",
            },
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["id"] == str(role.id)
        assert data["name"] == role.name
        assert data["scope"] == role.scope
        assert data["description"] == "updated_description"
        assert data["permissions"] == [101, 102]

    @pytest.mark.usefixtures("admin")
    def test_update_admin_role(self, client: TestClient):
        illegal = client.put(
            f"{ENDPOINT}/{ADMIN_UUID}",
            json={
                "permissions": [101, 102],
            },
        )
        assert illegal.status_code == 403
        assert (
            illegal.json()["detail"]
            == "You cannot change the permissions of the admin role"
        )

        legal = client.put(
            f"{ENDPOINT}/{ADMIN_UUID}",
            json={
                "description": "admins can have a custom description",
            },
        )
        assert legal.status_code == 200

        data = legal.json()
        assert data["id"] == str(ADMIN_UUID)
        assert data["scope"] == Scope.GLOBAL
        assert data["description"] == "admins can have a custom description"

    @pytest.mark.usefixtures("admin")
    def test_delete_role(self, client: TestClient):
        role: Role = RoleFactory(scope=Scope.DATASET)
        response = client.get(f"{ENDPOINT}/{role.scope}")
        assert response.status_code == 200
        roles_before = len(response.json()["roles"])

        response = client.delete(f"{ENDPOINT}/{role.id}")
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}/{role.scope}")
        assert response.status_code == 200
        assert roles_before - len(response.json()["roles"]) == 1
