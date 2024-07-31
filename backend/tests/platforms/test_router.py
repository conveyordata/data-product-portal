import json

from tests.factories import (
    PlatformFactory,
    PlatformServiceConfigFactory,
    PlatformServiceFactory,
    UserFactory,
)

ENDPOINT = "/api/platforms"


class TestPlatformsRouter:
    def test_get_all_platforms(self, client):
        UserFactory(external_id="sub", is_admin=True)
        platform = PlatformFactory()

        response = client.get(ENDPOINT)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == platform.name

    def test_get_platform_services(self, client):
        UserFactory(external_id="sub", is_admin=True)
        platform_service = PlatformServiceFactory()

        response = client.get(f"{ENDPOINT}/{platform_service.platform.id}/services")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == platform_service.name

    def test_get_platform_service_config_forbidden(self, client):
        response = client.get(
            f"{ENDPOINT}/b6801a56-121c-4dca-a0e9-7726d949ad79"
            f"/services/e34853ec-8320-4aae-8167-dc2730bd1fcb"
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Only admin can execute this operation"

    def test_get_platform_service_config(self, client):
        UserFactory(external_id="sub", is_admin=True)
        service = PlatformServiceFactory()
        config = PlatformServiceConfigFactory(
            platform=service.platform, service=service
        )

        response = client.get(
            f"{ENDPOINT}/{config.platform_id}/services/{config.service_id}"
        )

        assert response.status_code == 200
        fetched_config = response.json()
        expected_config = json.loads(config.config)
        assert fetched_config == {"config": expected_config}
        assert "identifiers" in expected_config
