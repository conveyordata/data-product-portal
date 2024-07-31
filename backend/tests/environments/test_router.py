import pytest
from sqlalchemy.exc import IntegrityError

from ..factories import EnvironmentFactory, UserFactory

ENDPOINT = "/api/envs"


class TestEnvironmentsRouter:
    def test_create_environment(self, client):
        UserFactory(external_id="sub", is_admin=True)
        response = self.create_environment(
            client,
            {"name": "dev", "context": "environment_context{{}}", "is_default": False},
        )
        assert response.status_code == 200

    def test_get_environments(self, client):
        UserFactory(external_id="sub", is_admin=True)
        env_obj = EnvironmentFactory()

        response = client.get(ENDPOINT)
        assert response.status_code == 200
        environments = response.json()
        assert len(environments) == 1
        assert environments[0]["name"] == env_obj.name

    def test_create_environment_with_repeated_name(self, client):
        UserFactory(external_id="sub", is_admin=True)
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
