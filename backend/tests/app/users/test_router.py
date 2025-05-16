import pytest
from tests.factories import UserFactory

ENDPOINT = "/api/users"


class TestUsersRouter:
    def test_get_users(self, client):
        UserFactory()

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["is_admin"] is False

    def test_remove_user_not_admin(self, client):
        user = UserFactory()

        response = client.delete(f"{ENDPOINT}/{user.id}")
        assert response.status_code == 403

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()) == 2

    @pytest.mark.usefixtures("admin")
    def test_remove_user(self, client):
        user = UserFactory()

        response = client.get(f"{ENDPOINT}")
        print(response.json())
        response = client.delete(f"{ENDPOINT}/{user.id}")
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert user.id not in [u["id"] for u in response.json()]

    def test_post_user_not_admin(self, client):
        response = client.post(f"{ENDPOINT}")
        assert response.status_code == 403

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.usefixtures("admin")
    def test_post_user(self, client):
        response = client.post(
            f"{ENDPOINT}",
            json={
                "email": "test@user.com",
                "external_id": "test-user",
                "first_name": "test",
                "last_name": "user",
                "is_admin": False,
            },
        )
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()) == 2

    @pytest.mark.usefixtures("admin")
    def test_post_user_default_admin(self, client):
        response = client.post(
            f"{ENDPOINT}",
            json={
                "email": "test@user.com",
                "external_id": "test-user",
                "first_name": "test",
                "last_name": "user",
            },
        )
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()) == 2
