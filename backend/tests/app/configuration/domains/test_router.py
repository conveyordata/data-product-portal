from uuid import uuid4

import pytest

from tests.factories import (
    DataProductFactory,
    DomainFactory,
    EnvironmentFactory,
    ExplorationFactory,
)

ENDPOINT = "/api/v2/configuration/domains"


@pytest.fixture
def domain_payload():
    return {"name": "Test Domain", "description": "Test Description"}


class TestDomainsRouter:
    @pytest.mark.usefixtures("admin")
    def test_create_domain(self, domain_payload, client):
        response = self.create_domain(client, domain_payload)
        assert response.status_code == 200
        assert "id" in response.json()

    def test_get_domains(self, client):
        domain = DomainFactory()
        ExplorationFactory(domain=domain)
        DataProductFactory(domain=domain)
        domains = self.get_domains(client)
        assert domains.status_code == 200
        assert len(domains.json()["domains"]) == 1
        assert domains.json()["domains"][0]["abstract_data_product_count"] == 2

    def test_get_domain(self, client):
        domain = DomainFactory()
        response = self.get_domain(client, domain.id)
        assert response.status_code == 200
        assert response.json()["id"] == str(domain.id)
        assert response.json()["environments"] == []

    @pytest.mark.usefixtures("admin")
    def test_create_domain__with_environments(self, client):
        environment = EnvironmentFactory()
        payload = {
            "name": "Test Domain",
            "description": "Test Description",
            "environment_ids": [str(environment.id)],
        }
        response = self.create_domain(client, payload)
        assert response.status_code == 200, response.text

        domain_response = self.get_domain(client, response.json()["id"])
        assert [env["id"] for env in domain_response.json()["environments"]] == [
            str(environment.id)
        ]

    @pytest.mark.usefixtures("admin")
    def test_create_domain__invalid_environment_id(self, client, domain_payload):
        domain_payload["environment_ids"] = [str(uuid4())]
        response = self.create_domain(client, domain_payload)
        assert response.status_code == 400

    @pytest.mark.usefixtures("admin")
    def test_update_domain(self, client):
        domain = DomainFactory()
        update_payload = {"name": "update", "description": "update"}
        response = self.update_domain(client, update_payload, domain.id)
        assert response.status_code == 200
        assert response.json()["id"] == str(domain.id)

    @pytest.mark.usefixtures("admin")
    def test_update_domain__sets_custom_environments(self, client):
        environment = EnvironmentFactory()
        domain = DomainFactory()
        update_payload = {
            "name": "update",
            "description": "update",
            "environment_ids": [str(environment.id)],
        }
        response = self.update_domain(client, update_payload, domain.id)
        assert response.status_code == 200

        domain_response = self.get_domain(client, domain.id)
        assert [env["id"] for env in domain_response.json()["environments"]] == [
            str(environment.id)
        ]

    @pytest.mark.usefixtures("admin")
    def test_update_domain__clearing_environments_reverts_to_global(self, client):
        environment = EnvironmentFactory()
        domain = DomainFactory(environments=[environment])
        update_payload = {
            "name": "update",
            "description": "update",
            "environment_ids": [],
        }
        response = self.update_domain(client, update_payload, domain.id)
        assert response.status_code == 200

        domain_response = self.get_domain(client, domain.id)
        assert domain_response.json()["environments"] == []

    @pytest.mark.usefixtures("admin")
    def test_remove_domain(self, client):
        domain = DomainFactory()
        response = self.remove_domain(client, domain.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_remove_domain_coupled_data_product(self, client):
        domain = DomainFactory()
        DataProductFactory(domain=domain)
        response = self.remove_domain(client, domain.id)
        assert response.status_code == 400

    @pytest.mark.usefixtures("admin")
    def test_migrate_domains(self, client):
        domain = DomainFactory()
        new_domain = DomainFactory()
        data_product = DataProductFactory(domain=domain)
        exploration = ExplorationFactory(domain=domain)
        response = self.migrate_domains(client, domain.id, new_domain.id)
        assert response.status_code == 200
        assert data_product.domain.id == new_domain.id
        assert exploration.domain.id == new_domain.id

    def test_create_domain_admin_only(self, domain_payload, client):
        response = self.create_domain(client, domain_payload)
        assert response.status_code == 403

    def test_update_domain_admin_only(self, client):
        domain = DomainFactory()
        update_payload = {"name": "update", "description": "update"}
        response = self.update_domain(client, update_payload, domain.id)
        assert response.status_code == 403

    def test_remove_domain_admin_only(self, client):
        domain = DomainFactory()
        response = self.remove_domain(client, domain.id)
        assert response.status_code == 403

    def test_migrate_domains_admin_only(self, client):
        domain = DomainFactory()
        new_domain = DomainFactory()
        response = self.migrate_domains(client, domain.id, new_domain.id)
        assert response.status_code == 403

    @staticmethod
    def create_domain(client, payload):
        return client.post(ENDPOINT, json=payload)

    @staticmethod
    def get_domain(client, domain_id):
        return client.get(f"{ENDPOINT}/{domain_id}")

    @staticmethod
    def update_domain(client, payload, domain_id):
        return client.put(f"{ENDPOINT}/{domain_id}", json=payload)

    @staticmethod
    def remove_domain(client, domain_id):
        return client.delete(f"{ENDPOINT}/{domain_id}")

    @staticmethod
    def get_domains(client):
        return client.get(ENDPOINT)

    @staticmethod
    def migrate_domains(client, from_id, to_id):
        return client.put(f"{ENDPOINT}/migrate/{from_id}/{to_id}")
