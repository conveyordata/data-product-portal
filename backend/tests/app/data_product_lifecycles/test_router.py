import pytest
from tests.factories import DataProductFactory, LifecycleFactory

ENDPOINT = "/api/data_product_lifecycles"


class TestDataProductLifecyclesRouter:
    @pytest.mark.usefixtures("admin")
    def test_create_data_product_lifecycle(self, client):
        response = self.create_data_product_lifecycle(
            client, {"name": "test", "value": 2, "color": "blue"}
        )
        assert response.status_code == 200
        assert "id" in response.json()

    def test_get_data_product_lifecycles(self, client):
        LifecycleFactory()
        response = self.get_data_product_lifecycles(client)
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.usefixtures("admin")
    def test_update_data_product_lifecycle(self, client):
        data_product_lifecycle = LifecycleFactory()
        update_payload = {"name": "update", "value": 3, "color": "green"}
        response = self.update_data_product_lifecycle(
            client, update_payload, data_product_lifecycle.id
        )
        assert response.status_code == 200
        assert response.json()["id"] == str(data_product_lifecycle.id)

    @pytest.mark.usefixtures("admin")
    def test_remove_data_product_lifecycle(self, client):
        data_product_lifecycle = LifecycleFactory()
        response = self.remove_data_product_lifecycle(client, data_product_lifecycle.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_remove_data_product_lifecycle_coupled_data_product(self, client):
        data_product_lifecycle = LifecycleFactory()
        DataProductFactory(lifecycle=data_product_lifecycle)
        response = self.remove_data_product_lifecycle(client, data_product_lifecycle.id)
        assert response.status_code == 200

    def test_create_data_product_lifecycle_admin_only(self, client):
        response = self.create_data_product_lifecycle(
            client, {"name": "test", "value": 2, "color": "blue"}
        )
        assert response.status_code == 403

    def test_update_data_product_lifecycle_admin_only(self, client):
        data_product_lifecycle = LifecycleFactory()
        update_payload = {
            "name": "update",
            "description": "update",
        }
        response = self.update_data_product_lifecycle(
            client, update_payload, data_product_lifecycle.id
        )
        assert response.status_code == 403

    def test_remove_data_product_lifecycle_admin_only(self, client):
        data_product_lifecycle = LifecycleFactory()
        response = self.remove_data_product_lifecycle(client, data_product_lifecycle.id)
        assert response.status_code == 403

    @staticmethod
    def create_data_product_lifecycle(client, data_product_lifecycle_payload):
        return client.post(ENDPOINT, json=data_product_lifecycle_payload)

    @staticmethod
    def get_data_product_lifecycle(client, lifecycle_id):
        return client.get(f"{ENDPOINT}/{lifecycle_id}")

    @staticmethod
    def update_data_product_lifecycle(client, payload, data_product_lifecycle_id):
        return client.put(f"{ENDPOINT}/{data_product_lifecycle_id}", json=payload)

    @staticmethod
    def remove_data_product_lifecycle(client, data_product_lifecycle_id):
        return client.delete(f"{ENDPOINT}/{data_product_lifecycle_id}")

    @staticmethod
    def get_data_product_lifecycles(client):
        return client.get(ENDPOINT)

    @staticmethod
    def migrate_data_product_lifecycles(client, from_id, to_id):
        return client.put(f"{ENDPOINT}/migrate/{from_id}/{to_id}")
