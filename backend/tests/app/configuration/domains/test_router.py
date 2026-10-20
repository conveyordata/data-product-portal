import pytest
from sqlalchemy import select

from app.data_products.model import DataProductEnvironment
from app.authorization.roles.schema import Scope
from app.configuration.domains.status import DomainStatus
from app.core.authz import Action
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.model import DataProductVisibility
from app.database.database import UNFILTERED
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    DomainFactory,
    EnvironmentFactory,
    ExplorationFactory,
    GlobalRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from tests.webhook_util import assert_event_in_queue

ENDPOINT = "/api/v2/configuration/domains"


@pytest.fixture
def configuration_manager():
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    role = RoleFactory(
        scope=Scope.GLOBAL, permissions=[Action.GLOBAL__UPDATE_CONFIGURATION]
    )
    GlobalRoleAssignmentFactory(identity_id=user.id, role_id=role.id)
    return user


@pytest.fixture
def domain_payload():
    return {
        "name": "Test Domain",
        "namespace": "test-domain",
        "description": "Test Description",
    }


class TestDomainsRouter:
    @pytest.mark.usefixtures("admin")
    def test_create_domain(self, domain_payload, client):
        response = self.create_domain(client, domain_payload)
        assert response.status_code == 200
        assert "id" in response.json()

    @pytest.mark.usefixtures("admin")
    def test_create_domain__emits_event(self, domain_payload, client, capture_events):
        response = self.create_domain(client, domain_payload)
        assert response.status_code == 200
        assert_event_in_queue("domain.event", capture_events)

    @pytest.mark.usefixtures("admin")
    def test_create_domain__duplicate_namespace(self, domain_payload, client):
        DomainFactory(namespace=domain_payload["namespace"])
        response = self.create_domain(client, domain_payload)
        assert response.status_code == 400

    @pytest.mark.usefixtures("admin")
    def test_create_domain__dots_only_namespace(self, domain_payload, client):
        domain_payload["namespace"] = ".."
        response = self.create_domain(client, domain_payload)
        assert response.status_code == 400

    @pytest.mark.usefixtures("admin")
    def test_create_domain__invalid_namespace(self, domain_payload, client):
        domain_payload["namespace"] = "Invalid Namespace!"
        response = self.create_domain(client, domain_payload)
        assert response.status_code == 400

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
        assert response.json()["namespace"] == domain.namespace
        assert response.json()["status"] == DomainStatus.ACTIVE
        assert response.json()["finalizers"] == []

    @pytest.mark.usefixtures("admin")
    def test_create_domain__with_environments(self, client):
        environment = EnvironmentFactory()
        payload = {
            "name": "Test Domain",
            "namespace": "test-domain",
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
        assert "environments" not in response.json()

    @pytest.mark.usefixtures("admin")
    def test_update_domain(self, client):
        domain = DomainFactory()
        update_payload = {"name": "update", "description": "update"}
        response = self.update_domain(client, update_payload, domain.id)
        assert response.status_code == 200
        assert response.json()["id"] == str(domain.id)

    @pytest.mark.usefixtures("admin")
    def test_update_domain__emits_event(self, client, capture_events):
        domain = DomainFactory()
        update_payload = {"name": "update", "description": "update"}
        response = self.update_domain(client, update_payload, domain.id)
        assert response.status_code == 200
        assert_event_in_queue("domain.event", capture_events)

    @pytest.mark.usefixtures("admin")
    def test_update_domain__namespace_is_immutable(self, client):
        domain = DomainFactory(namespace="original")
        update_payload = {"name": "update", "description": "update", "namespace": "new"}
        response = self.update_domain(client, update_payload, domain.id)
        assert response.status_code == 200
        assert self.get_domain(client, domain.id).json()["namespace"] == "original"

    @pytest.mark.usefixtures("admin")
    def test_update_domain__deleting(self, client):
        domain = DomainFactory(status=DomainStatus.DELETING, finalizers=["x"])
        update_payload = {"name": "update", "description": "update"}
        response = self.update_domain(client, update_payload, domain.id)
        assert response.status_code == 409

    @pytest.mark.usefixtures("admin")
    def test_update_domain__environments_emit_event(self, client, capture_events):
        environment = EnvironmentFactory()
        domain = DomainFactory(name="same", description="same")
        update_payload = {
            "name": "same",
            "description": "same",
            "environment_ids": [str(environment.id)],
        }
        response = self.update_domain(client, update_payload, domain.id)
        assert response.status_code == 200
        assert_event_in_queue("domain.event", capture_events)

    @pytest.mark.usefixtures("admin")
    def test_update_domain__preserves_data_product_environments(self, client):
        environment = EnvironmentFactory()
        domain = DomainFactory()
        product = DataProductFactory(
            domain=domain,
            environments=[DataProductEnvironment(environment=environment)],
        )
        before = self.get_data_product_environments(client, product.id)
        update_payload = {
            "name": "update",
            "description": "update",
        }
        response = self.update_domain(client, update_payload, domain.id)
        assert response.status_code == 200

        assert self.get_data_product_environments(client, product.id) == before

    @pytest.mark.usefixtures("admin")
    def test_remove_domain(self, client):
        domain = DomainFactory()
        response = self.remove_domain(client, domain.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_remove_domain__emits_event(self, client, capture_events):
        domain = DomainFactory()
        response = self.remove_domain(client, domain.id)
        assert response.status_code == 200
        assert_event_in_queue("domain.event", capture_events)

    @pytest.mark.usefixtures("admin")
    def test_remove_domain_coupled_data_product(self, client):
        domain = DomainFactory()
        DataProductFactory(domain=domain)
        response = self.remove_domain(client, domain.id)
        assert response.status_code == 400

    @pytest.mark.usefixtures("configuration_manager")
    def test_remove_domain__hidden_data_product_blocks_non_admin(self, client):
        domain = DomainFactory(finalizers=["provisioner"])
        DataProductFactory(domain=domain, visibility=DataProductVisibility.HIDDEN)
        response = self.remove_domain(client, domain.id)
        assert response.status_code == 400
        assert self.get_domain(client, domain.id).json()["status"] == (
            DomainStatus.ACTIVE
        )

    @pytest.mark.usefixtures("configuration_manager")
    def test_get_domains__counts_hidden_data_products_for_non_admin(self, client):
        domain = DomainFactory()
        DataProductFactory(domain=domain, visibility=DataProductVisibility.HIDDEN)
        response = self.get_domains(client)
        assert response.json()["domains"][0]["abstract_data_product_count"] == 1

    @pytest.mark.usefixtures("configuration_manager")
    def test_migrate_domains__moves_hidden_data_products_for_non_admin(
        self, client, session
    ):
        domain = DomainFactory()
        new_domain = DomainFactory()
        data_product = DataProductFactory(
            domain=domain, visibility=DataProductVisibility.HIDDEN
        )
        response = self.migrate_domains(client, domain.id, new_domain.id)
        assert response.status_code == 200
        assert (
            session.scalar(
                select(DataProductModel.domain_id).where(
                    DataProductModel.id == data_product.id
                ),
                execution_options=UNFILTERED,
            )
            == new_domain.id
        )

    @pytest.mark.usefixtures("admin")
    def test_remove_domain__with_finalizers_marks_deleting(self, client):
        domain = DomainFactory(finalizers=["provisioner"])
        response = self.remove_domain(client, domain.id)
        assert response.status_code == 202
        domain_response = self.get_domain(client, domain.id).json()
        assert domain_response["status"] == DomainStatus.DELETING
        assert domain_response["finalizers"] == ["provisioner"]

    @pytest.mark.usefixtures("admin")
    def test_remove_domain__with_finalizers_and_data_product(self, client):
        domain = DomainFactory(finalizers=["provisioner"])
        DataProductFactory(domain=domain)
        response = self.remove_domain(client, domain.id)
        assert response.status_code == 400
        assert self.get_domain(client, domain.id).json()["status"] == (
            DomainStatus.ACTIVE
        )

    @pytest.mark.usefixtures("admin")
    def test_remove_finalizer__last_one_after_delete_request_deletes_domain(
        self, client, capture_events
    ):
        domain = DomainFactory(finalizers=["provisioner"])
        assert self.remove_domain(client, domain.id).status_code == 202
        response = self.remove_finalizer(client, domain.id, "provisioner")
        assert response.status_code == 200
        assert self.get_domain(client, domain.id).status_code == 404
        assert_event_in_queue("domain.event", capture_events)

    @pytest.mark.usefixtures("admin")
    def test_remove_finalizer__last_one_on_already_deleting_domain_deletes_it(
        self, client
    ):
        domain = DomainFactory(status=DomainStatus.DELETING, finalizers=["provisioner"])
        response = self.remove_finalizer(client, domain.id, "provisioner")
        assert response.status_code == 200
        assert self.get_domain(client, domain.id).status_code == 404

    @pytest.mark.usefixtures("admin")
    def test_remove_finalizer__not_deleting_keeps_domain(self, client):
        domain = DomainFactory(finalizers=["a", "b"])
        response = self.remove_finalizer(client, domain.id, "a")
        assert response.status_code == 200
        assert self.get_domain(client, domain.id).json()["finalizers"] == ["b"]

    @pytest.mark.usefixtures("admin")
    def test_remove_finalizer__unknown(self, client):
        domain = DomainFactory()
        response = self.remove_finalizer(client, domain.id, "unknown")
        assert response.status_code == 404

    @pytest.mark.usefixtures("admin")
    def test_add_finalizer__idempotent(self, client):
        domain = DomainFactory()
        assert self.add_finalizer(client, domain.id, "provisioner").status_code == 200
        assert self.add_finalizer(client, domain.id, "provisioner").status_code == 200
        assert self.get_domain(client, domain.id).json()["finalizers"] == [
            "provisioner"
        ]

    @pytest.mark.usefixtures("admin")
    def test_add_finalizer__unknown_domain(self, client):
        response = self.add_finalizer(client, uuid4(), "provisioner")
        assert response.status_code == 404

    @pytest.mark.usefixtures("admin")
    def test_remove_finalizer__unknown_domain(self, client):
        response = self.remove_finalizer(client, uuid4(), "provisioner")
        assert response.status_code == 404

    @pytest.mark.usefixtures("admin")
    def test_add_finalizer__deleting(self, client):
        domain = DomainFactory(status=DomainStatus.DELETING, finalizers=["a"])
        response = self.add_finalizer(client, domain.id, "b")
        assert response.status_code == 409

    def test_add_finalizer__requires_permission(self, client):
        domain = DomainFactory()
        response = self.add_finalizer(client, domain.id, "provisioner")
        assert response.status_code == 403

    def test_remove_finalizer__requires_permission(self, client):
        domain = DomainFactory(finalizers=["provisioner"])
        response = self.remove_finalizer(client, domain.id, "provisioner")
        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    def test_migrate_domains__to_deleting_domain(self, client):
        domain = DomainFactory()
        new_domain = DomainFactory(status=DomainStatus.DELETING, finalizers=["a"])
        DataProductFactory(domain=domain)
        response = self.migrate_domains(client, domain.id, new_domain.id)
        assert response.status_code == 409

    @pytest.mark.usefixtures("admin")
    def test_migrate_domains(self, client):
        domain = DomainFactory()
        new_domain = DomainFactory()
        environment = EnvironmentFactory()
        data_product = DataProductFactory(
            domain=domain,
            environments=[DataProductEnvironment(environment=environment)],
        )
        before = self.get_data_product_environments(client, data_product.id)
        exploration = ExplorationFactory(domain=domain)
        response = self.migrate_domains(client, domain.id, new_domain.id)
        assert response.status_code == 200
        assert data_product.domain.id == new_domain.id
        assert exploration.domain.id == new_domain.id
        assert self.get_data_product_environments(client, data_product.id) == before

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
    def get_data_product_environments(client, data_product_id):
        response = client.get(f"/api/v2/data_products/{data_product_id}")
        assert response.status_code == 200, response.text
        return response.json()["environments"]

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
    def add_finalizer(client, domain_id, finalizer):
        return client.post(
            f"{ENDPOINT}/{domain_id}/finalizers", json={"finalizer": finalizer}
        )

    @staticmethod
    def remove_finalizer(client, domain_id, finalizer):
        return client.delete(f"{ENDPOINT}/{domain_id}/finalizers/{finalizer}")

    @staticmethod
    def get_domains(client):
        return client.get(ENDPOINT)

    @staticmethod
    def migrate_domains(client, from_id, to_id):
        return client.put(f"{ENDPOINT}/migrate/{from_id}/{to_id}")
