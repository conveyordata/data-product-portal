import json

import pytest
from sqlalchemy.exc import IntegrityError

from ..factories import (
    EnvironmentFactory,
    EnvPlatformServiceConfigFactory,
    PlatformServiceConfigFactory,
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
        assert response.status_code == 201

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

    @pytest.mark.usefixtures("admin")
    def test_get_environment(self, client):
        env = EnvironmentFactory()
        response = client.get(f"{ENDPOINT}/{env.id}")
        assert response.status_code == 200
        assert response.json()["name"] == env.name

    def test_get_environment_platform_service_config_forbidden(self, client):
        response = client.get(f"{ENDPOINT}/configs/config_uuid")
        assert response.status_code == 403
        assert response.json()["detail"] == "Only admin can execute this operation"

    @pytest.mark.usefixtures("admin")
    def test_get_environment_platform_service_config(self, client):
        service = PlatformServiceFactory()
        config_obj = EnvPlatformServiceConfigFactory(
            platform=service.platform, service=service
        )

        response = client.get(f"{ENDPOINT}/configs/{config_obj.id}")

        assert response.status_code == 200
        actual_config = response.json()
        assert actual_config["config"] == json.loads(config_obj.config)

    def test_get_environment_configs_forbidden(self, client):
        response = client.get(f"{ENDPOINT}/env_uuid/configs")
        assert response.status_code == 403
        assert response.json()["detail"] == "Only admin can execute this operation"

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

    def test_create_config_forbidden(self, client):
        response = client.post(f"{ENDPOINT}/environment_uuid/configs", json={})
        assert response.status_code == 403
        assert response.json()["detail"] == "Only admin can execute this operation"

    @pytest.mark.usefixtures("admin")
    def test_create_failed_no_pltfrm_srvc_config(self, client):
        service = PlatformServiceFactory()
        env = EnvironmentFactory()

        response = client.post(
            f"{ENDPOINT}/{env.id}/configs",
            json={
                "platform_id": str(service.platform.id),
                "service_id": str(service.id),
                "config": {},
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "There's no platform service configuration"

    @pytest.mark.usefixtures("admin")
    def test_create_failed_invalid_config(self, client):
        service = PlatformServiceFactory()
        PlatformServiceConfigFactory(
            platform=service.platform,
            service=service,
            config='{"identifiers": ["random_name"]}',
        )
        env = EnvironmentFactory()

        response = client.post(
            f"{ENDPOINT}/{env.id}/configs",
            json={
                "platform_id": str(service.platform.id),
                "service_id": str(service.id),
                "config": {},
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid configuration"

    @pytest.mark.usefixtures("admin")
    def test_create_config(self, client):
        service = PlatformServiceFactory()
        PlatformServiceConfigFactory(platform=service.platform, service=service)
        env = EnvironmentFactory()

        response = client.post(
            f"{ENDPOINT}/{env.id}/configs",
            json={
                "platform_id": str(service.platform.id),
                "service_id": str(service.id),
                "config": {
                    "bucket_1": {
                        "account_id": 10,
                        "name": "test_name",
                        "arn": "test_arn",
                        "kms": "test_kms",
                    }
                },
            },
        )
        assert response.status_code == 201
