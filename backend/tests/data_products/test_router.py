from app.data_product_memberships.enums import DataProductUserRole

ENDPOINT = "/api/data_products"


class TestDataProductsRouter:
    invalid_data_product_id = "00000000-0000-0000-0000-000000000000"

    def test_create_data_product(self, client, default_data_product_payload):
        created_data_product = self.create_default_data_product(
            client, default_data_product_payload
        )
        assert created_data_product.status_code == 200
        assert "id" in created_data_product.json()

    def test_get_data_products(self, client, default_data_product_payload):
        created_data_product = self.create_default_data_product(
            client, default_data_product_payload
        )
        assert created_data_product.status_code == 200

        data_product = client.get(ENDPOINT)
        assert data_product.status_code == 200
        assert len(data_product.json()) == 1

    def test_update_data_product(
        self, client, session, default_data_product, default_data_product_payload
    ):
        created_data_product = self.create_default_data_product(
            client, default_data_product_payload
        )
        assert created_data_product.status_code == 200
        assert "id" in created_data_product.json()

        data_product = self.get_data_product_by_id(
            client, created_data_product.json()["id"]
        )
        assert data_product.status_code == 200
        assert "id" in data_product.json()
        data_product_data = data_product.json()

        updated_data_product = self.update_default_data_product(
            client, default_data_product, data_product_data["id"]
        )

        assert updated_data_product.status_code == 200
        assert "id" in updated_data_product.json()

    def test_update_data_product_about(
        self, client, session, default_data_product_payload
    ):
        created_data_product = self.create_default_data_product(
            client, default_data_product_payload
        )
        assert created_data_product.status_code == 200
        assert "id" in created_data_product.json()

        data_product = self.get_data_product_by_id(
            client, created_data_product.json()["id"]
        )
        assert data_product.status_code == 200
        assert "id" in data_product.json()
        data_product_data = data_product.json()

        updated_data_product_about = self.update_data_product_about(
            client, data_product_data["id"]
        )
        assert updated_data_product_about.status_code == 200

    def test_remove_data_product(self, client, session, default_data_product_payload):
        created_data_product = self.create_default_data_product(
            client, default_data_product_payload
        )
        assert created_data_product.status_code == 200
        assert "id" in created_data_product.json()

        data_product_data = created_data_product.json()
        deleted_data_product = self.delete_default_data_product(
            client, data_product_data["id"]
        )
        assert deleted_data_product.status_code == 200

    def test_get_data_product_by_id_with_invalid_id(self, client):
        data_product = self.get_data_product_by_id(client, self.invalid_data_product_id)
        assert data_product.status_code == 404

    def test_update_data_product_with_invalid_data_product_id(
        self, client, default_data_product
    ):
        data_product = self.update_default_data_product(
            client, default_data_product, self.invalid_data_product_id
        )
        assert data_product.status_code == 404

    def test_remove_data_product_with_invalid_data_product_id(self, client):
        data_product = self.delete_default_data_product(
            client, self.invalid_data_product_id
        )
        assert data_product.status_code == 404

    @staticmethod
    def default_update_data_product_payload(default_data_product):
        return {
            "name": "Updated Data Product Name",
            "description": "Updated Data Product Description",
            "external_id": "Updated Data Product External ID",
            "tags": [
                {"value": "Updated tag"},
            ],
            "type_id": str(default_data_product.type_id),
            "memberships": [
                {
                    "user_id": str(default_data_product.memberships[0].user_id),
                    "role": DataProductUserRole.OWNER.value,
                }
            ],
            "business_area_id": str(default_data_product.business_area_id),
        }

    @staticmethod
    def default_data_product_about_payload():
        return {"about": "Updated Data Product Description"}

    @staticmethod
    def create_default_data_product(client, default_data_product_payload):
        response = client.post(ENDPOINT, json=default_data_product_payload)
        return response

    def update_default_data_product(
        self, client, default_data_product, data_product_id
    ):
        data = self.default_update_data_product_payload(default_data_product)
        response = client.put(f"{ENDPOINT}/{data_product_id}", json=data)
        return response

    @staticmethod
    def update_data_product_about(client, data_product_id):
        data = TestDataProductsRouter.default_data_product_about_payload()
        response = client.put(f"{ENDPOINT}/{data_product_id}/about", json=data)
        return response

    @staticmethod
    def delete_default_data_product(client, data_product_id):
        response = client.delete(f"{ENDPOINT}/{data_product_id}")
        return response

    @staticmethod
    def get_data_product_by_id(client, data_product_id):
        response = client.get(f"{ENDPOINT}/{data_product_id}")
        return response
