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

    @staticmethod
    def create_environment(client, environment):
        environment_dict = environment.model_dump()
        response = client.post(f"{ENDPOINT}", json=environment_dict)
        return response
