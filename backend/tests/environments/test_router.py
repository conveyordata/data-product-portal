import pytest
from sqlalchemy.exc import IntegrityError
from tests.factories import EnvironmentFactory, PlatformFactory, UserFactory

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
        response = client.post(ENDPOINT, json=environment_dict)
        return response

    def test_get_all_platforms(self, client):
        UserFactory(external_id="sub", is_admin=True)
        platform = PlatformFactory()

        response = client.get(f"{ENDPOINT}/{platform.env.name}/platforms")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == platform.name
        assert "settings" in data[0]

    def test_get_all_platforms_forbidden(self, client):
        response = client.get(f"{ENDPOINT}/dev/platforms")
        assert response.status_code == 403
        assert response.json()["detail"] == "Only admin can execute this operation"

    def test_delete_platform_forbidden(self, client):
        response = client.delete(f"{ENDPOINT}/platforms/platformID")
        assert response.status_code == 403
        assert response.json()["detail"] == "Only admin can execute this operation"

    def test_delete_platform(self, client):
        UserFactory(external_id="sub", is_admin=True)
        platform = PlatformFactory()
        env_name = platform.env.name

        response = client.delete(f"{ENDPOINT}/platforms/{platform.id}")
        assert response.status_code == 204

        response = client.get(f"{ENDPOINT}/{env_name}/platforms")
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_create_platform_forbidden(self, client):
        response = client.put(f"{ENDPOINT}/dev/platforms", json={})
        assert response.status_code == 403

    def test_create_platform(self, client):
        UserFactory(external_id="sub", is_admin=True)
        env = EnvironmentFactory()
        payload = {
            "name": "AWS",
            "settings": {
                "account_id": "accountId",
                "kms_key": "kmsKey",
                "s3": {"bucket_arn": "string", "prefix_path": "string"},
                "glue": {"schema": "string", "table_prefixes": ["string"]},
            },
        }

        response = client.put(f"{ENDPOINT}/{env.name}/platforms", json=payload)
        assert response.status_code == 201

        response = client.get(f"{ENDPOINT}/{env.name}/platforms?name={payload['name']}")
        platform = response.json()

        assert isinstance(platform, dict)
        assert platform["name"] == payload["name"]
        assert platform["settings"]["account_id"] == payload["settings"]["account_id"]
        assert platform["settings"]["kms_key"] == payload["settings"]["kms_key"]
        assert "id" in platform
        assert "s3" in platform["settings"]
        assert "glue" in platform["settings"]
