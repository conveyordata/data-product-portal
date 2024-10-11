import json

import pytest
from tests.factories import (
    PlatformFactory,
    PlatformServiceConfigFactory,
    PlatformServiceFactory,
)

ENDPOINT = "/api/platforms"


class TestPlatformsRouter:
    def test_get_all_platforms(self, client):
        platform = PlatformFactory()

        response = client.get(ENDPOINT)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == platform.name

    def test_get_platform_services(self, client):
        platform_service = PlatformServiceFactory()

        response = client.get(f"{ENDPOINT}/{platform_service.platform.id}/services")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == platform_service.name

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
