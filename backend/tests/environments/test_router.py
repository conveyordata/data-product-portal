import json

import pytest

from ..factories import (
    EnvironmentFactory,
    EnvPlatformConfigFactory,
    EnvPlatformServiceConfigFactory,
    PlatformServiceFactory,
)

ENDPOINT = "/api/envs"


class TestEnvironmentsRouter:
    @pytest.mark.usefixtures("admin")
    def test_get_environments(self, client):
        env_obj = EnvironmentFactory()

        response = client.get(ENDPOINT)
        assert response.status_code == 200
        environments = response.json()
        assert len(environments) == 1
        assert environments[0]["name"] == env_obj.name

    def test_get_environment_platform_service_config_forbidden(self, client):
        response = client.get(
            f"{ENDPOINT}/environment_uuid/platforms/platform_uuid"
            f"/services/service_id/config",
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Only admin can execute this operation"

    @pytest.mark.usefixtures("admin")
    def test_get_environment_platform_service_config(self, client):
        service = PlatformServiceFactory()
        config_obj = EnvPlatformServiceConfigFactory(
            platform=service.platform, service=service
        )
        response = client.get(
            f"{ENDPOINT}/{config_obj.environment_id}/platforms/{service.platform.id}"
            f"/services/{service.id}/config",
        )
        assert response.status_code == 200
        actual_config = response.json()
        assert actual_config["config"] == json.loads(config_obj.config)

    def test_get_environment_platform_config_forbidden(self, client):
        response = client.get(
            f"{ENDPOINT}/environment_uuid/platforms/platform_uuid/config",
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Only admin can execute this operation"

    @pytest.mark.usefixtures("admin")
    def test_get_environment_platform_config(self, client):
        config_obj = EnvPlatformConfigFactory()

        response = client.get(
            f"{ENDPOINT}/{config_obj.environment_id}/platforms"
            f"/{config_obj.platform.id}/config",
        )

        assert response.status_code == 200
        actual_config = response.json()
        assert actual_config["config"] == json.loads(config_obj.config)

    @pytest.mark.usefixtures("admin")
    def test_get_environment_configs(self, client):
        service = PlatformServiceFactory()
        config_obj = EnvPlatformServiceConfigFactory(
            platform=service.platform, service=service
        )

        response = client.get(f"{ENDPOINT}/{config_obj.environment_id}/configs")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["service"]["name"] == service.name
        assert "platform" in data[0]
        assert "config" in data[0]
