import json
import uuid

import pytest

from tests.factories import (
    EnvironmentFactory,
    EnvPlatformConfigFactory,
    EnvPlatformServiceConfigFactory,
    PlatformServiceFactory,
)

ENDPOINT = "/api/v2/configuration/environments"


class TestEnvironmentsRouter:
    @pytest.mark.usefixtures("admin")
    def test_get_environments(self, client):
        env_obj = EnvironmentFactory()

        response = client.get(ENDPOINT)
        assert response.status_code == 200
        environments = response.json()
        assert len(environments["environments"]) == 1
        assert environments["environments"][0]["name"] == env_obj.name

    def test_get_environment(self, client):
        env_obj = EnvironmentFactory()

        response = self.get_environment_by_id(client, env_obj.id)
        assert response.status_code == 200
        actual_env = response.json()
        assert actual_env["name"] == env_obj.name

    @pytest.mark.usefixtures("admin")
    def test_get_platform_service_configs(self, client):
        service = PlatformServiceFactory()
        config_obj = EnvPlatformServiceConfigFactory(
            platform=service.platform, service=service
        )
        EnvPlatformServiceConfigFactory(
            platform=service.platform,
            service=service,
            environment=EnvironmentFactory(name="production"),
        )
        response = client.get(
            f"{ENDPOINT}/platforms/{service.platform.id}/services/{service.id}/config",
        )

        assert response.status_code == 200
        actual_config = response.json()
        assert len(actual_config["environment_configs"]) == 2
        assert actual_config["environment_configs"][0]["config"] == json.loads(
            config_obj.config
        )

    @pytest.mark.usefixtures("admin")
    def test_get_config(self, client):
        service = PlatformServiceFactory()
        config_obj = EnvPlatformServiceConfigFactory(
            platform=service.platform, service=service
        )
        response = client.get(f"{ENDPOINT}/configs/{config_obj.id}")
        assert response.status_code == 200
        actual_config = response.json()
        assert actual_config["config"] == json.loads(config_obj.config)

    def test_get_environment_platform_service_config_forbidden(self, client):
        response = client.get(
            f"{ENDPOINT}/environment_uuid/platforms/platform_uuid"
            f"/services/service_id/config",
        )
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "You don't have permission to perform this action"
        )

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

    @pytest.mark.usefixtures("admin")
    def test_get_environment_platform_config_forbidden(self, client):
        response = client.get(
            f"{ENDPOINT}/environment_uuid/platforms/platform_uuid/config",
        )
        assert response.status_code == 422

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
        assert len(data["environment_configs"]) == 1
        assert data["environment_configs"][0]["service"]["name"] == service.name
        assert "platform" in data["environment_configs"][0]
        assert "config" in data["environment_configs"][0]

    @pytest.mark.usefixtures("admin")
    def test_update_environment_is_global__toggles_flag(self, client):
        EnvironmentFactory()
        env_obj = EnvironmentFactory(name="production")

        response = self.update_environment_is_global(client, env_obj.id, False)
        assert response.status_code == 200
        assert response.json()["is_global"] is False

    @pytest.mark.usefixtures("admin")
    def test_update_environment_is_global__allows_removing_last_global(self, client):
        env_obj = EnvironmentFactory()

        response = self.update_environment_is_global(client, env_obj.id, False)
        assert response.status_code == 200
        assert response.json()["is_global"] is False

    def test_update_environment_is_global_forbidden(self, client):
        env_obj = EnvironmentFactory()

        response = self.update_environment_is_global(client, env_obj.id, False)
        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    def test_get_environments__orders_by_name_when_no_position_set(self, client):
        for name in ["tst", "prd", "dev"]:
            EnvironmentFactory(name=name)

        assert self.environment_names(client) == ["dev", "prd", "tst"]

    @pytest.mark.usefixtures("admin")
    def test_get_environments__orders_by_position(self, client):
        for name, position in [("dev", 3), ("tst", 1), ("prd", 2)]:
            EnvironmentFactory(name=name, position=position)

        assert self.environment_names(client) == ["tst", "prd", "dev"]

    @pytest.mark.usefixtures("admin")
    def test_get_environments__orders_unset_positions_last_by_name(self, client):
        EnvironmentFactory(name="aaa")
        EnvironmentFactory(name="prd", position=2)
        EnvironmentFactory(name="bbb")
        EnvironmentFactory(name="dev", position=1)

        assert self.environment_names(client) == ["dev", "prd", "aaa", "bbb"]

    @pytest.mark.usefixtures("admin")
    def test_update_environment_position__sets_and_clears_position(self, client):
        env_obj = EnvironmentFactory()

        response = self.update_environment_position(client, env_obj.id, 5)
        assert response.status_code == 200
        assert response.json()["position"] == 5

        response = self.update_environment_position(client, env_obj.id, None)
        assert response.status_code == 200
        assert response.json()["position"] is None

    @pytest.mark.usefixtures("admin")
    def test_update_environment__keeps_fields_not_sent(self, client):
        env_obj = EnvironmentFactory(is_global=True, position=3)

        response = self.update_environment_position(client, env_obj.id, 1)
        assert response.json()["is_global"] is True

        response = self.update_environment_is_global(client, env_obj.id, False)
        assert response.json()["position"] == 1

    @pytest.mark.usefixtures("admin")
    def test_update_environment__rejects_null_is_global(self, client):
        env_obj = EnvironmentFactory()

        response = self.update_environment_is_global(client, env_obj.id, None)
        assert response.status_code == 422

    @pytest.mark.usefixtures("admin")
    def test_update_environment_position__not_found(self, client):
        response = self.update_environment_position(client, uuid.uuid4(), 1)
        assert response.status_code == 404

    def test_update_environment_position_forbidden(self, client):
        env_obj = EnvironmentFactory()

        response = self.update_environment_position(client, env_obj.id, 1)
        assert response.status_code == 403

    @staticmethod
    def environment_names(client):
        response = client.get(ENDPOINT)
        assert response.status_code == 200
        return [env["name"] for env in response.json()["environments"]]

    @staticmethod
    def update_environment_position(client, environment_id, position):
        return client.patch(f"{ENDPOINT}/{environment_id}", json={"position": position})

    @staticmethod
    def get_environment_by_id(client, environment_id):
        return client.get(f"{ENDPOINT}/{environment_id}")

    @staticmethod
    def update_environment_is_global(client, environment_id, is_global):
        return client.patch(
            f"{ENDPOINT}/{environment_id}", json={"is_global": is_global}
        )
