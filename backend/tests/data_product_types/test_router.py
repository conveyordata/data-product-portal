from tests.factories import DataProductTypeFactory

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
