import json

import pytest
from sqlalchemy.exc import IntegrityError

from ..factories import (
    EnvironmentFactory,
    EnvPlatformConfigFactory,
    EnvPlatformServiceConfigFactory,
    PlatformServiceFactory,
    UserFactory,
)

ENDPOINT = "/api/envs"


class TestEnvironmentsRouter:
    def test_create_environment(self, client):
        UserFactory(external_id="sub", is_admin=True)
        response = self.create_environment(
            client,
            {"name": "dev", "context": "environment_context{{}}", "is_default": False},
        )
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_get_environments(self, client):
        env_obj = EnvironmentFactory()

        response = client.get(ENDPOINT)
        assert response.status_code == 200
        environments = response.json()
        assert len(environments) == 1
        assert environments[0]["name"] == env_obj.name

    @pytest.mark.usefixtures("admin")
    def test_create_environment_with_repeated_name(self, client):
        env_obj = EnvironmentFactory()
        with pytest.raises(IntegrityError):
            self.create_environment(
                client,
                {
                    "name": env_obj.name,
                    "context": "environment_context{{}}",
                    "is_default": False,
                },
            )

    @staticmethod
    def create_environment(client, environment):
        response = client.post(ENDPOINT, json=environment)
        return response

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
