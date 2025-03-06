import pytest

ENDPOINT = "/api/theme_settings"


@pytest.fixture
def update_payload():
    return {"portal_name": "Updated"}


class TestThemeSettingsRouter:
    def test_get_settings(self, client):
        settings = client.get(ENDPOINT)
        assert settings.status_code == 200

    def test_update_settings_admin_only(self, client, update_payload):
        response = self.update_settings(client, update_payload)
        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    def test_update_settings(self, client, update_payload):
        response = self.update_settings(client, update_payload)
        assert response.status_code == 200

    @staticmethod
    def get_settings(client):
        return client.get(ENDPOINT)

    @staticmethod
    def update_settings(client, payload):
        return client.put(ENDPOINT, json=payload)
