from tests.factories import DataProductTypeFactory
from tests.factories.data_product import DataProductFactory

from app.data_product_types.enums import DataProductIconKey

ENDPOINT = "/api/data_product_types"


class TestDataProductTypesRouter:

    def test_create_data_product_type(self, client):
        data = {
            "name": "Test Data Product Type",
            "description": "Test Description",
            "icon_key": DataProductIconKey.DEFAULT.value,
        }
        response = client.post(ENDPOINT, json=data)
        assert response.status_code == 200
        assert "id" in response.json()

    def test_get_data_product_types(self, client):
        DataProductTypeFactory()
        response = client.get(ENDPOINT)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_data_product_type(self, client):
        data_product_type = DataProductTypeFactory()
        response = self.get_data_product_type(client, data_product_type.id)
        assert response.status_code == 200
        assert response.json()["id"] == str(data_product_type.id)

    def test_update_data_product_type(self, client):
        data_product_type = DataProductTypeFactory()
        update_payload = {
            "name": "update",
            "description": "update",
            "icon_key": DataProductIconKey.DEFAULT.value,
        }
        response = self.update_data_product_type(
            client, update_payload, data_product_type.id
        )
        assert response.status_code == 200
        assert response.json()["id"] == str(data_product_type.id)

    def test_remove_data_product_type(self, client):
        data_product_type = DataProductTypeFactory()
        response = self.remove_data_product_type(client, data_product_type.id)
        assert response.status_code == 200

    def test_remove_data_product_type_coupled_data_product(self, client):
        data_product_type = DataProductTypeFactory()
        DataProductFactory(type=data_product_type)
        response = self.remove_data_product_type(client, data_product_type.id)
        assert response.status_code == 400

    def test_migrate_data_product_types(self, client):
        data_product_type = DataProductTypeFactory()
        new_data_product_type = DataProductTypeFactory()
        data_product = DataProductFactory(type=data_product_type)
        response = self.migrate_data_product_types(
            client, data_product_type.id, new_data_product_type.id
        )
        assert response.status_code == 200
        assert data_product.type.id == new_data_product_type.id

    @staticmethod
    def create_data_product_type(client, data_product_type_payload):
        return client.post(ENDPOINT, json=data_product_type_payload)

    @staticmethod
    def get_data_product_type(client, data_product_type_id):
        return client.get(f"{ENDPOINT}/{data_product_type_id}")

    @staticmethod
    def update_data_product_type(client, payload, data_product_type_id):
        return client.put(f"{ENDPOINT}/{data_product_type_id}", json=payload)

    @staticmethod
    def remove_data_product_type(client, data_product_type_id):
        return client.delete(f"{ENDPOINT}/{data_product_type_id}")

    @staticmethod
    def get_data_product_types(client):
        return client.get(ENDPOINT)

    @staticmethod
    def migrate_data_product_types(client, from_id, to_id):
        return client.put(f"{ENDPOINT}/migrate/{from_id}/{to_id}")
