import pytest
from tests.factories import BusinessAreaFactory

ENDPOINT = "/api/business_areas"


@pytest.fixture
def business_area_payload():
    return {"name": "Test Business Area", "description": "Test Description"}


class TestBusinessAreasRouter:

    def test_create_business_area(self, business_area_payload, client):
        response = client.post(ENDPOINT, json=business_area_payload)
        assert response.status_code == 200
        assert "id" in response.json()

    def test_get_business_areas(self, client):
        BusinessAreaFactory()
        business_areas = client.get(ENDPOINT)
        assert business_areas.status_code == 200
        assert len(business_areas.json()) == 1
