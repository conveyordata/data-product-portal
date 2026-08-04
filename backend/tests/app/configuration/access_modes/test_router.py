import pytest

from tests.factories import AccessModeFactory

ENDPOINT = "/api/v2/configuration/access_modes"


@pytest.fixture
def access_mode_payload():
    return {
        "name": "Test Access Mode",
        "description": "Test Description",
    }


class TestAccessModesRouter:
    @pytest.mark.usefixtures("admin")
    def test_create_access_mode(self, access_mode_payload, client):
        response = self.create_access_mode(client, access_mode_payload)
        assert response.status_code == 200
        assert "id" in response.json()

    @pytest.mark.usefixtures("admin")
    def test_update_access_mode(self, client):
        access_mode = AccessModeFactory()
        response = self.update_access_mode(
            client, {"description": "Updated Description"}, access_mode.id
        )
        assert response.status_code == 200
        assert response.json()["id"] == str(access_mode.id)

    def test_get_access_modes(self, client):
        AccessModeFactory()
        response = self.get_access_modes(client)
        assert response.status_code == 200
        assert len(response.json()["access_modes"]) == 1

    @staticmethod
    def create_access_mode(client, payload):
        return client.post(ENDPOINT, json=payload)

    @staticmethod
    def update_access_mode(client, payload, access_mode_id):
        return client.put(f"{ENDPOINT}/{access_mode_id}", json=payload)

    @staticmethod
    def get_access_modes(client):
        return client.get(ENDPOINT)
