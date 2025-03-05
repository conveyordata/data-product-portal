import pytest
from tests.factories import RoleFactory

from app.roles.model import Role

ENDPOINT = "/api/roles"


class TestRolesRouter:

    test_role = {
        "name": "test",
        "scope": "dataset",
        "description": "test description",
        "permissions": [101],
    }

    def test_get_roles(self, client):
        role: Role = RoleFactory(scope="global")
        response = client.get(f"{ENDPOINT}/global")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["scope"] == role.scope

    @pytest.mark.usefixtures("admin")
    def test_create_role(self, client):
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
    def test_update_role(self, client):
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
    def test_delete_role(self, client):
        role: Role = RoleFactory()
        response = client.get(f"{ENDPOINT}/{role.scope}")
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = client.delete(f"{ENDPOINT}/{role.id}")
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}/{role.scope}")
        assert response.status_code == 200
        assert len(response.json()) == 0
