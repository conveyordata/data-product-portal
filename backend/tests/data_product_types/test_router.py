from app.data_product_types.enums import DataProductIconKey
from app.data_product_types.schema import DataProductTypeCreate

ENDPOINT = "/api/data_product_types"


class TestDataProductTypesRouter:

    def test_create_data_product_type(self, client, session):
        response = self.create_default_product_type(client)
        assert response.status_code == 200
        assert "id" in response.json()

    def test_get_data_product_types(self, client, session):
        response = self.create_default_product_type(client)
        assert response.status_code == 200

        business_areas = client.get(ENDPOINT)
        assert business_areas.status_code == 200
        assert len(business_areas.json()) == 1

    @staticmethod
    def default_data_product_type_payload():
        return DataProductTypeCreate(
            name="Test Data Product Type",
            description="Test Description",
            icon_key=DataProductIconKey.DEFAULT.value,
        )

    def create_default_product_type(self, client):
        data = self.default_data_product_type_payload()
        response = client.post(ENDPOINT, json=data.model_dump())
        return response
