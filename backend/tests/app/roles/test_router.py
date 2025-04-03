import pytest
from fastapi.testclient import TestClient
from tests.factories import RoleFactory

from app.roles.schema import Prototype, Role, Scope
from app.roles.service import ADMIN_UUID

ENDPOINT = "/api/roles"


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
        assert len(data) == 1
        assert data[0]["scope"] == role.scope

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
    def test_update_role(self, client: TestClient):
        role: Role = RoleFactory()
        response = client.patch(
            ENDPOINT,
            json={
                "id": str(role.id),
                "permissions": [101, 102],
                "description": "updated_description",
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == str(role.id)
        assert data["name"] == role.name
        assert data["scope"] == role.scope
        assert data["description"] == "updated_description"
        assert data["permissions"] == [101, 102]

    @pytest.mark.usefixtures("admin")
    def test_update_admin_role(self, client: TestClient):
        admin: Role = RoleFactory(
            scope=Scope.GLOBAL, prototype=Prototype.ADMIN, id=ADMIN_UUID
        )
        illegal = client.patch(
            ENDPOINT,
            json={
                "id": str(admin.id),
                "permissions": [101, 102],
            },
        )
        assert illegal.status_code == 403
        assert (
            illegal.json()["detail"]
            == "You cannot change the permissions of the admin role"
        )

        legal = client.patch(
            ENDPOINT,
            json={
                "id": str(admin.id),
                "description": "admins can have a custom description",
            },
        )
        assert legal.status_code == 200

        data = legal.json()
        assert data["id"] == str(admin.id)
        assert data["name"] == admin.name
        assert data["scope"] == admin.scope
        assert data["description"] == "admins can have a custom description"

    @pytest.mark.usefixtures("admin")
    def test_delete_role(self, client: TestClient):
        role: Role = RoleFactory()
        response = client.get(f"{ENDPOINT}/{role.scope}")
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = client.delete(f"{ENDPOINT}/{role.id}")
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}/{role.scope}")
        assert response.status_code == 200
        assert len(response.json()) == 0
