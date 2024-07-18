ENDPOINT = "/api/users"


class TestUsersRouter:
    def test_get_users(self, client, default_user):
        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["is_admin"] is False

    def test_remove_user(self, client, default_user):
        response = client.delete(f"{ENDPOINT}/{default_user.id}")
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()) == 0
