import pytest

ENDPOINT = "/api/general_settings"


class TestGeneralSettingsRouter:
    def test_get_settings(self, client):
        settings = client.get(ENDPOINT)
        assert settings.status_code == 200

    def test_update_settings_admin_only(self, client):
        payload = {"portal_name": "Updated"}

        response = self.update_settings(client, payload)
        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    def test_update_settings(self, client):
        payload = {"portal_name": "Updated"}

        response = self.update_settings(client, payload)
        assert response.status_code == 200

    @staticmethod
    def get_settings(client):
        return client.get(ENDPOINT)

    @staticmethod
    def update_settings(client, payload):
        return client.put(ENDPOINT, json=payload)
