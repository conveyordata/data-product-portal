import pytest

from tests.factories import (
    EnvironmentFactory,
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

    @staticmethod
    def get_environment_by_id(client, environment_id):
        return client.get(f"{ENDPOINT}/{environment_id}")

    @staticmethod
    def update_environment_is_global(client, environment_id, is_global):
        return client.patch(
            f"{ENDPOINT}/{environment_id}", json={"is_global": is_global}
        )
