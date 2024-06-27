from app.business_areas.schema import BusinessAreaCreate

ENDPOINT = "/api/business_areas"


class TestBusinessAreasRouter:

    def test_create_business_area(self, client, session):
        response = self.create_default_business_area(client)
        assert response.status_code == 200
        assert "id" in response.json()

    def test_get_business_areas(self, client, session):
        response = self.create_default_business_area(client)
        assert response.status_code == 200

        business_areas = client.get(ENDPOINT)
        assert business_areas.status_code == 200
        assert len(business_areas.json()) == 1

    @staticmethod
    def default_business_area_payload():
        return BusinessAreaCreate(
            name="Test Business Area",
            description="Test Description",
        )

    def create_default_business_area(self, client):
        data = self.default_business_area_payload()
        response = client.post(ENDPOINT, json=data.model_dump())
        return response
