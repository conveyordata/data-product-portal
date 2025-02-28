import pytest
from tests.factories import DataProductSettingFactory

ENDPOINT = "/api/data_product_settings"


@pytest.fixture
def default_setting_payload():
    return {
        "external_id": "external_id",
        "tooltip": "tooltip",
        "name": "name",
        "type": "checkbox",
        "category": "category",
        "default": "True",
        "order": 1,
        "scope": "dataproduct",
    }


class TestDataProductSettingsRouter:
    @pytest.mark.usefixtures("admin")
    def test_create_data_product_setting(self, default_setting_payload, client):
        response = self.create_data_product_setting(client, default_setting_payload)
        assert response.status_code == 200
        assert "id" in response.json()

    def test_get_data_product_settings(self, client):
        DataProductSettingFactory()
        response = self.get_data_product_settings(client)
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.usefixtures("admin")
    def test_update_data_product_setting(self, client):
        data_product_setting = DataProductSettingFactory()
        update_payload = {
            "external_id": "update",
            "tooltip": "tooltip",
            "name": "name",
            "type": "checkbox",
            "category": "category",
            "default": "False",
            "order": 3,
            "scope": "dataproduct",
        }
        response = self.update_data_product_setting(
            client, update_payload, data_product_setting.id
        )
        assert response.status_code == 200
        assert response.json()["id"] == str(data_product_setting.id)

    @pytest.mark.usefixtures("admin")
    def test_remove_data_product_setting(self, client):
        data_product_setting = DataProductSettingFactory()
        response = self.remove_data_product_setting(client, data_product_setting.id)
        assert response.status_code == 200

    def test_create_data_product_setting_admin_only(
        self, default_setting_payload, client
    ):
        response = self.create_data_product_setting(client, default_setting_payload)
        assert response.status_code == 403

    def test_update_data_product_setting_admin_only(self, client):
        data_product_setting = DataProductSettingFactory()
        update_payload = {
            "name": "update",
            "description": "update",
        }
        response = self.update_data_product_setting(
            client, update_payload, data_product_setting.id
        )
        assert response.status_code == 403

    def test_remove_data_product_setting_admin_only(self, client):
        data_product_setting = DataProductSettingFactory()
        response = self.remove_data_product_setting(client, data_product_setting.id)
        assert response.status_code == 403

    @staticmethod
    def create_data_product_setting(client, data_product_setting_payload):
        return client.post(ENDPOINT, json=data_product_setting_payload)

    @staticmethod
    def get_data_product_setting(client, lifecycle_id):
        return client.get(f"{ENDPOINT}/{lifecycle_id}")

    @staticmethod
    def update_data_product_setting(client, payload, data_product_setting_id):
        return client.put(f"{ENDPOINT}/{data_product_setting_id}", json=payload)

    @staticmethod
    def remove_data_product_setting(client, data_product_setting_id):
        return client.delete(f"{ENDPOINT}/{data_product_setting_id}")

    @staticmethod
    def get_data_product_settings(client):
        return client.get(ENDPOINT)

    @staticmethod
    def migrate_data_product_settings(client, from_id, to_id):
        return client.put(f"{ENDPOINT}/migrate/{from_id}/{to_id}")
