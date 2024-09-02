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

    def test_get_platform_service_config_forbidden(self, client):
        response = client.get(
            f"{ENDPOINT}/b6801a56-121c-4dca-a0e9-7726d949ad79"
            f"/services/e34853ec-8320-4aae-8167-dc2730bd1fcb"
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Only admin can execute this operation"

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
        data = response.json()
        expected_config = json.loads(config.config)
        assert "platform" in data
        assert data["config"] == expected_config
        assert data["service"]["name"] == service.name

    def test_create_platform_service_config_forbidden(self, client):
        response = client.post(f"{ENDPOINT}/platform_uuid/services/service_uuid")
        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    def test_create_platform_service_config(self, client):
        service = PlatformServiceFactory()
        response = client.post(
            f"{ENDPOINT}/{service.platform.id}/services/{service.id}",
            json={"identifiers": ["bucket_name"]},
        )

        assert response.status_code == 201

    def test_get_platforms_configs_forbidden(self, client):
        response = client.get(f"{ENDPOINT}/configs")
        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    def test_get_platforms_configs(self, client):
        service = PlatformServiceFactory()
        config = PlatformServiceConfigFactory(
            platform=service.platform, service=service
        )

        response = client.get(f"{ENDPOINT}/configs")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "platform" in data[0]
        assert data[0]["service"]["name"] == service.name
        assert data[0]["config"] == json.loads(config.config)

    def test_get_platform_service_config_by_id_forbidden(self, client):
        response = client.get(f"{ENDPOINT}/configs/config_uuid")
        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    def test_get_platform_service_config_by_id(self, client):
        service = PlatformServiceFactory()
        config = PlatformServiceConfigFactory(
            platform=service.platform, service=service
        )

        response = client.get(f"{ENDPOINT}/configs/{config.id}")

        assert response.status_code == 200
        data = response.json()
        assert "platform" in data
        assert data["service"]["name"] == service.name
        assert data["config"] == json.loads(config.config)
