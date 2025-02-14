import pytest
from tests.factories import BusinessAreaFactory
from tests.factories.data_product import DataProductFactory
from tests.factories.dataset import DatasetFactory

ENDPOINT = "/api/business_areas"


@pytest.fixture
def business_area_payload():
    return {"name": "Test Business Area", "description": "Test Description"}


class TestBusinessAreasRouter:

    def test_create_business_area(self, business_area_payload, client):
        response = self.create_business_area(client, business_area_payload)
        assert response.status_code == 200
        assert "id" in response.json()

    def test_get_business_areas(self, client):
        BusinessAreaFactory()
        business_areas = self.get_business_areas(client)
        assert business_areas.status_code == 200
        assert len(business_areas.json()) == 1

    def test_get_business_area(self, client):
        business_area = BusinessAreaFactory()
        response = self.get_business_area(client, business_area.id)
        assert response.status_code == 200
        assert response.json()["id"] == str(business_area.id)

    def test_update_business_area(self, client):
        business_area = BusinessAreaFactory()
        update_payload = {"name": "update", "description": "update"}
        response = self.update_business_area(client, update_payload, business_area.id)
        assert response.status_code == 200
        assert response.json()["id"] == str(business_area.id)

    def test_remove_business_area(self, client):
        business_area = BusinessAreaFactory()
        response = self.remove_business_area(client, business_area.id)
        assert response.status_code == 200

    def test_remove_business_area_coupled_data_product(self, client):
        business_area = BusinessAreaFactory()
        DataProductFactory(business_area=business_area)
        response = self.remove_business_area(client, business_area.id)
        assert response.status_code == 400

    def test_remove_business_area_coupled_dataset(self, client):
        business_area = BusinessAreaFactory()
        DatasetFactory(business_area=business_area)
        response = self.remove_business_area(client, business_area.id)
        assert response.status_code == 400

    def test_migrate_business_areas(self, client):
        business_area = BusinessAreaFactory()
        new_business_area = BusinessAreaFactory()
        data_product = DataProductFactory(business_area=business_area)
        dataset = DatasetFactory(business_area=business_area)
        response = self.migrate_business_areas(
            client, business_area.id, new_business_area.id
        )
        assert response.status_code == 200
        assert data_product.business_area.id == new_business_area.id
        assert dataset.business_area.id == new_business_area.id

    @staticmethod
    def create_business_area(client, business_area_payload):
        return client.post(ENDPOINT, json=business_area_payload)

    @staticmethod
    def get_business_area(client, business_area_id):
        return client.get(f"{ENDPOINT}/{business_area_id}")

    @staticmethod
    def update_business_area(client, payload, business_area_id):
        return client.put(f"{ENDPOINT}/{business_area_id}", json=payload)

    @staticmethod
    def remove_business_area(client, business_area_id):
        return client.delete(f"{ENDPOINT}/{business_area_id}")

    @staticmethod
    def get_business_areas(client):
        return client.get(ENDPOINT)

    @staticmethod
    def migrate_business_areas(client, from_id, to_id):
        return client.put(f"{ENDPOINT}/migrate/{from_id}/{to_id}")
