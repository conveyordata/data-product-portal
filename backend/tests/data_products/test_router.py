from copy import deepcopy

import pytest
from tests.factories import (
    BusinessAreaFactory,
    DataProductFactory,
    DataProductTypeFactory,
    TagFactory,
    UserFactory,
)
from tests.factories.data_output import DataOutputFactory
from tests.factories.data_product_membership import DataProductMembershipFactory

from app.data_product_memberships.enums import DataProductUserRole

ENDPOINT = "/api/data_products"


@pytest.fixture
def payload():
    business_area = BusinessAreaFactory()
    data_product_type = DataProductTypeFactory()
    user = UserFactory()
    tag = TagFactory()
    return {
        "name": "Data Product Name",
        "description": "Updated Data Product Description",
        "external_id": "Updated Data Product External ID",
        "tag_ids": [
            str(tag.id),
        ],
        "type_id": str(data_product_type.id),
        "memberships": [
            {
                "user_id": str(user.id),
                "role": DataProductUserRole.OWNER.value,
            }
        ],
        "business_area_id": str(business_area.id),
    }


class TestDataProductsRouter:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def test_create_data_product(self, payload, client):
        created_data_product = self.create_data_product(client, payload)
        assert created_data_product.status_code == 200
        assert "id" in created_data_product.json()

    def test_get_data_products(self, client):
        data_product = DataProductFactory()
        response = client.get(ENDPOINT)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(data_product.id)

    def test_get_data_product_by_id(self, client):
        data_product = DataProductFactory()

        response = self.get_data_product_by_id(client, data_product.id)
        assert response.status_code == 200
        assert response.json()["id"] == str(data_product.id)

    def test_get_conveyor_ide_url(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductMembershipFactory(user=user).data_product

        response = self.get_conveyor_ide_url(client, data_product.id)
        assert response.status_code == 501

    def test_get_data_product_by_user_id(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductMembershipFactory(user=user).data_product

        response = self.get_data_product_by_user_id(client, user.id)
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == str(data_product.id)

    def test_get_data_outputs(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductMembershipFactory(user=user).data_product
        data_output = DataOutputFactory(owner=data_product)
        response = self.get_data_outputs(client, data_product.id)
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == str(data_output.id)

    def test_update_data_product_no_member(self, payload, client):
        data_product = DataProductFactory()
        update_payload = deepcopy(payload)
        update_payload["name"] = "Updated Data Product"
        response = self.update_data_product(client, update_payload, data_product.id)

        assert response.status_code == 403

    def test_update_data_product(self, payload, client):
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
        update_payload = deepcopy(payload)
        update_payload["name"] = "Updated Data Product"
        response = self.update_data_product(client, update_payload, data_product.id)

        assert response.status_code == 200
        assert response.json()["id"] == str(data_product.id)

    def test_update_data_product_about_no_member(self, client):
        data_product = DataProductFactory()
        response = self.update_data_product_about(client, data_product.id)
        assert response.status_code == 403

    def test_update_data_product_about(self, client):
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
        response = self.update_data_product_about(client, data_product.id)
        assert response.status_code == 200

    def test_remove_data_product_no_member(self, client):
        data_product = DataProductFactory()
        response = self.delete_data_product(client, data_product.id)
        assert response.status_code == 403

    def test_remove_data_product(self, client):
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
        response = self.delete_data_product(client, data_product.id)
        assert response.status_code == 200

    def test_get_data_product_by_id_with_invalid_id(self, client):
        data_product = self.get_data_product_by_id(client, self.invalid_id)
        assert data_product.status_code == 404

    def test_update_data_product_with_invalid_data_product_id(self, client, payload):
        data_product = self.update_data_product(client, payload, self.invalid_id)
        assert data_product.status_code == 404

    def test_remove_data_product_with_invalid_data_product_id(self, client):
        data_product = self.delete_data_product(client, self.invalid_id)
        assert data_product.status_code == 404

    @staticmethod
    def create_data_product(client, default_data_product_payload):
        return client.post(ENDPOINT, json=default_data_product_payload)

    @staticmethod
    def update_data_product(client, payload, data_product_id):
        return client.put(f"{ENDPOINT}/{data_product_id}", json=payload)

    @staticmethod
    def update_data_product_about(client, data_product_id):
        data = {"about": "Updated Data Product Description"}
        return client.put(f"{ENDPOINT}/{data_product_id}/about", json=data)

    @staticmethod
    def delete_data_product(client, data_product_id):
        return client.delete(f"{ENDPOINT}/{data_product_id}")

    @staticmethod
    def get_data_product_by_id(client, data_product_id):
        return client.get(f"{ENDPOINT}/{data_product_id}")

    @staticmethod
    def get_data_outputs(client, data_product_id):
        return client.get(f"{ENDPOINT}/{data_product_id}/data_outputs")

    @staticmethod
    def get_data_product_by_user_id(client, user_id):
        return client.get(f"{ENDPOINT}/user/{user_id}")

    @staticmethod
    def get_conveyor_ide_url(client, data_product_id):
        return client.get(f"{ENDPOINT}/{data_product_id}/conveyor_ide_url")
