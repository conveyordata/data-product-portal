import pytest
from tests.factories import DomainFactory
from tests.factories.data_product import DataProductFactory
from tests.factories.dataset import DatasetFactory

ENDPOINT = "/api/domains"


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
        DomainFactory()
        domains = self.get_domains(client)
        assert domains.status_code == 200
        assert len(domains.json()) == 1

    def test_get_domain(self, client):
        domain = DomainFactory()
        response = self.get_domain(client, domain.id)
        assert response.status_code == 200
        assert response.json()["id"] == str(domain.id)

    @pytest.mark.usefixtures("admin")
    def test_update_domain(self, client):
        domain = DomainFactory()
        update_payload = {"name": "update", "description": "update"}
        response = self.update_domain(client, update_payload, domain.id)
        assert response.status_code == 200
        assert response.json()["id"] == str(domain.id)

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
    def test_remove_domain_coupled_dataset(self, client):
        domain = DomainFactory()
        DatasetFactory(domain=domain)
        response = self.remove_domain(client, domain.id)
        assert response.status_code == 400

    @pytest.mark.usefixtures("admin")
    def test_migrate_domains(self, client):
        domain = DomainFactory()
        new_domain = DomainFactory()
        data_product = DataProductFactory(domain=domain)
        dataset = DatasetFactory(domain=domain)
        response = self.migrate_domains(
            client, domain.id, new_domain.id
        )
        assert response.status_code == 200
        assert data_product.domain.id == new_domain.id
        assert dataset.domain.id == new_domain.id

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
        response = self.migrate_domains(
            client, domain.id, new_domain.id
        )
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
