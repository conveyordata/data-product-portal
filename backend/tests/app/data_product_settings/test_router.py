import pytest
from tests.factories import DataProductSettingFactory

from app.core.namespace.validation import NamespaceValidityType
from app.data_product_settings.enums import DataProductSettingScope

ENDPOINT = "/api/data_product_settings"


@pytest.fixture
def default_setting_payload():
    return {
        "namespace": "namespace",
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
            "namespace": "update",
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

    def test_get_namespace_suggestion_subsitution(self, client):
        name = "test with spaces"
        response = self.get_namespace_suggestion(client, name)
        body = response.json()

        assert response.status_code == 200
        assert body["namespace"] == "test-with-spaces"

    def test_get_namespace_length_limits(self, client):
        response = self.get_namespace_length_limits(client)
        assert response.status_code == 200
        assert response.json()["max_length"] > 1

    def test_validate_namespace(self, client):
        namespace = "test"
        response = self.validate_namespace(
            client, namespace, DataProductSettingScope.DATAPRODUCT
        )

        assert response.status_code == 200
        assert response.json()["validity"] == NamespaceValidityType.VALID

    def test_validate_namespace_invalid_characters(self, client):
        namespace = "!"
        response = self.validate_namespace(
            client, namespace, DataProductSettingScope.DATAPRODUCT
        )

        assert response.status_code == 200
        assert response.json()["validity"] == NamespaceValidityType.INVALID_CHARACTERS

    def test_validate_namespace_invalid_length(self, client):
        namespace = "a" * 256
        response = self.validate_namespace(
            client, namespace, DataProductSettingScope.DATAPRODUCT
        )

        assert response.status_code == 200
        assert response.json()["validity"] == NamespaceValidityType.INVALID_LENGTH

    def test_validate_namespace_duplicate(self, client):
        namespace = "test"
        DataProductSettingFactory(
            namespace=namespace, scope=DataProductSettingScope.DATAPRODUCT
        )
        response = self.validate_namespace(
            client, namespace, DataProductSettingScope.DATAPRODUCT
        )

        assert response.status_code == 200
        assert response.json()["validity"] == NamespaceValidityType.DUPLICATE_NAMESPACE

    def test_validate_namespace_duplicate_scoped_to_data_product(self, client):
        namespace = "test"
        DataProductSettingFactory(
            namespace=namespace, scope=DataProductSettingScope.DATAPRODUCT
        )
        response = self.validate_namespace(
            client, namespace, DataProductSettingScope.DATASET
        )

        assert response.status_code == 200
        assert response.json()["validity"] == NamespaceValidityType.VALID

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

    @staticmethod
    def get_namespace_suggestion(client, name):
        return client.get(f"{ENDPOINT}/namespace_suggestion?name={name}")

    @staticmethod
    def validate_namespace(client, namespace, scope: DataProductSettingScope):
        return client.get(
            f"{ENDPOINT}/validate_namespace?namespace={namespace}&scope={scope.value}"
        )

    @staticmethod
    def get_namespace_length_limits(client):
        return client.get(f"{ENDPOINT}/namespace_length_limits")
