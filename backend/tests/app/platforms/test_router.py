import json

import pytest

from tests.factories import (
    PlatformFactory,
    PlatformServiceConfigFactory,
    PlatformServiceFactory,
)

ENDPOINT = "/api/v2/configuration/platforms"


class TestPlatformsRouter:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def test_get_all_platforms(self, session, client):
        platform = PlatformFactory()

        response = client.get(ENDPOINT)

        assert response.status_code == 200
        data = response.json()
        assert len(data["platforms"]) == 1
        assert data["platforms"][0]["name"] == platform.name

    def test_get_platform_service_not_found(self, client):
        platform_service = PlatformServiceFactory()

        response = client.get(
            f"{ENDPOINT}/{platform_service.platform_id}/services/{self.invalid_id}"
        )

        assert response.status_code == 404

    def test_get_platform_services(self, client):
        platform_service = PlatformServiceFactory()

        response = client.get(f"{ENDPOINT}/{platform_service.platform.id}/services")

        assert response.status_code == 200
        data = response.json()
        assert len(data["platform_services"]) == 1
        assert data["platform_services"][0]["name"] == platform_service.name

    def test_get_platform_configs(self, client):
        platform_service = PlatformServiceFactory()
        config = PlatformServiceConfigFactory(
            platform=platform_service.platform, service=platform_service
        )

        response = client.get(f"{ENDPOINT}/configs")

        assert response.status_code == 200
        data = response.json()
        assert len(data["platform_service_configurations"]) == 1
        assert (
            data["platform_service_configurations"][0]["platform"]["name"]
            == platform_service.platform.name
        )
        assert (
            data["platform_service_configurations"][0]["service"]["name"]
            == platform_service.name
        )
        assert data["platform_service_configurations"][0]["config"] == json.loads(
            config.config
        )

    def test_get_platform_service(self, client):
        platform_service = PlatformServiceFactory()
        config = PlatformServiceConfigFactory(
            platform=platform_service.platform, service=platform_service
        )

        response = client.get(f"{ENDPOINT}/configs/{config.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["platform"]["name"] == platform_service.platform.name
        assert data["service"]["name"] == platform_service.name
        assert data["config"] == json.loads(config.config)

    @pytest.mark.usefixtures("admin")
    def test_get_platform_service_config(self, client):
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
        assert fetched_config["config"] == expected_config
