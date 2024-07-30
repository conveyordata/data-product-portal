import pytest
from sqlalchemy.exc import IntegrityError

ENDPOINT = "/api/envs"


class TestEnvironmentsRouter:
    def test_create_environment(self, client, session, default_environments):
        for environment in default_environments:
            response = self.create_environment(client, environment)
            assert response.status_code == 200

    def test_get_environments(self, client, session, default_environments):
        for environment in default_environments:
            response = self.create_environment(client, environment)
            assert response.status_code == 200

        environments = client.get(ENDPOINT)
        assert environments.status_code == 200
        assert len(environments.json()) == len(default_environments)

    def test_create_environment_with_repeated_name(
        self, client, session, default_environments
    ):
        for environment in default_environments:
            response = self.create_environment(client, environment)
            assert response.status_code == 200

        repeated_environment = default_environments[0]
        with pytest.raises(IntegrityError):
            self.create_environment(client, repeated_environment)

    @staticmethod
    def create_environment(client, environment):
        environment_dict = environment.model_dump()
        response = client.post(f"{ENDPOINT}", json=environment_dict)
        return response
