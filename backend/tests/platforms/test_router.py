from tests.factories import PlatformFactory, PlatformServiceFactory, UserFactory

ENDPOINT = "/api/platforms"


class TestPlatformsRouter:
    def test_get_all_platforms_forbidden(self, client):
        response = client.get(ENDPOINT)
        assert response.status_code == 403
        assert response.json()["detail"] == "Only admin can execute this operation"

    def test_get_all_platforms(self, client):
        UserFactory(external_id="sub", is_admin=True)
        platform = PlatformFactory()

        response = client.get(ENDPOINT)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == platform.name

    def test_get_platform_services_forbidden(self, client):
        response = client.get(f"{ENDPOINT}/AWS/services")
        assert response.status_code == 403
        assert response.json()["detail"] == "Only admin can execute this operation"

    def test_platform_services(self, client):
        UserFactory(external_id="sub", is_admin=True)
        platform_service = PlatformServiceFactory()

        response = client.get(f"{ENDPOINT}/{platform_service.platform.id}/services")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == platform_service.name
