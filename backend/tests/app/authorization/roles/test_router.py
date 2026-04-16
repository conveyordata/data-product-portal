import pytest
from fastapi.testclient import TestClient

from app.authorization.roles import ADMIN_UUID
from app.authorization.roles.schema import Role, Scope
from tests.factories import RoleFactory

ENDPOINT = "/api/v2/authz/roles"


class TestRolesRouter:
    test_role = {
        "name": "test",
        "scope": "dataset",
        "description": "test description",
        "permissions": [101],
    }

    def test_get_roles(self, client: TestClient):
        role: Role = RoleFactory(scope="global")
        response = client.get(f"{ENDPOINT}/global")

        assert response.status_code == 200
        data = response.json()
        assert len(data["roles"]) == 1
        assert data["roles"][0]["scope"] == role.scope

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
        assert data["permissions"] == self.test_role["permissions"]

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
    def test_update_role(self, client: TestClient):
        role: Role = RoleFactory()
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
        assert len(response.json()["roles"]) == 1

        response = client.delete(f"{ENDPOINT}/{role.id}")
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}/{role.scope}")
        assert response.status_code == 200
        assert len(response.json()["roles"]) == 0
