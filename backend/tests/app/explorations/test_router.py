import uuid

import faker

from app.authorization.roles.schema import Scope
from app.core.authz import Action
from app.settings import settings
from tests.factories import (
    DomainFactory,
    GlobalRoleAssignmentFactory,
    InputPortFactory,
    OutputPortFactory,
    RoleFactory,
    UserFactory,
)
from tests.factories.exploration import ExplorationFactory
from tests.webhook_util import assert_event_in_queue

ROUTE = "/api/v2/explorations"


class TestExplorationRouter:
    def test_create_exploration(self, client):
        d = DomainFactory()
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__CREATE_EXPLORATION],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )

        response = client.post(
            ROUTE,
            json={
                "name": str(uuid.uuid4()),
                "namespace": str(uuid.uuid4()),
                "domain_id": str(d.id),
                "description": faker.Faker().text(),
            },
        )
        assert response.status_code == 200, response.text

    def test_create_exploration_invalid_namespace(self, client):
        d = DomainFactory()
        namespace = str(uuid.uuid4())
        ExplorationFactory(namespace=namespace)

        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__CREATE_EXPLORATION],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )

        response = client.post(
            ROUTE,
            json={
                "name": str(uuid.uuid4()),
                "namespace": namespace,
                "domain_id": str(d.id),
                "description": faker.Faker().text(),
            },
        )
        assert response.status_code == 400, response.text

    def test_create_exploration_with_input_ports(self, client):
        d = DomainFactory()
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__CREATE_EXPLORATION],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )

        response = client.post(
            ROUTE,
            json={
                "name": str(uuid.uuid4()),
                "namespace": str(uuid.uuid4()),
                "domain_id": str(d.id),
                "description": faker.Faker().text(),
                "input_ports": {
                    "output_ports": [str(OutputPortFactory().id)],
                    "justification": "I am your king!",
                },
            },
        )
        assert response.status_code == 200, response.text

    def test_get_explorations(self, client):
        exploration = ExplorationFactory()
        response = client.get(ROUTE)
        assert response.status_code == 200, response.text
        assert len(response.json()["explorations"]) == 1
        assert response.json()["explorations"][0]["id"] == str(exploration.id)

    def test_get_explorations_filter_assignment(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        exploration = ExplorationFactory(owner=user)
        ExplorationFactory()
        response = client.get(
            ROUTE,
            params={
                "filter_to_user_with_assigment": str(user.id),
            },
        )
        assert response.status_code == 200, response.text
        assert len(response.json()["explorations"]) == 1
        assert response.json()["explorations"][0]["id"] == str(exploration.id)

    def test_get_exploration(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        exploration = ExplorationFactory(owner=user)
        response = client.get(f"{ROUTE}/{exploration.id}")
        assert response.status_code == 200, response.text
        assert response.json()["id"] == str(exploration.id)

    def test_get_exploration_input_ports(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        exploration = ExplorationFactory(owner=user)
        ExplorationFactory()
        InputPortFactory(consuming_abstract_data_product=exploration)
        response = client.get(f"{ROUTE}/{exploration.id}/input_ports")
        assert response.status_code == 200, response.text
        assert len(response.json()["input_ports"]) == 1

    def test_request_input_ports_for_exploration(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        exploration = ExplorationFactory(owner=user)
        response = client.post(
            f"{ROUTE}/{exploration.id}/input_ports",
            json={
                "output_ports": [str(OutputPortFactory().id)],
                "justification": "I am your king!",
            },
        )
        assert response.status_code == 200, response.text
        assert len(response.json()["input_port_ids"]) == 1

    def test_request_input_ports_for_exploration_event(self, mock_webhook, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        exploration = ExplorationFactory(owner=user)
        response = client.post(
            f"{ROUTE}/{exploration.id}/input_ports",
            json={
                "output_ports": [str(OutputPortFactory().id)],
                "justification": "I am your king!",
            },
        )
        assert response.status_code == 200, response.text
        assert len(response.json()["input_port_ids"]) == 1
        assert_event_in_queue("input_port.event", mock_webhook)

    def test_request_input_ports_for_exploration_does_not_exist(self, client):
        response = client.post(
            f"{ROUTE}/{uuid.uuid4()}/input_ports",
            json={
                "output_ports": [str(OutputPortFactory().id)],
                "justification": "I am your king!",
            },
        )
        assert response.status_code == 404, response.text

    def test_request_input_ports_for_exploration_not_owner(self, client):
        exploration = ExplorationFactory()
        response = client.post(
            f"{ROUTE}/{exploration.id}/input_ports",
            json={
                "output_ports": [str(OutputPortFactory().id)],
                "justification": "I am your king!",
            },
        )
        assert response.status_code == 403, response.text

    def test_remove_input_port_from_exploration(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        exploration = ExplorationFactory(owner=user)
        input_port = InputPortFactory(consuming_abstract_data_product=exploration)
        response = client.delete(
            f"{ROUTE}/{exploration.id}/input_ports/{input_port.dataset.id}",
        )
        assert response.status_code == 200, response.text

    def test_remove_input_port_from_exploration_not_owner(self, client):
        exploration = ExplorationFactory()
        input_port = InputPortFactory(consuming_abstract_data_product=exploration)
        response = client.delete(
            f"{ROUTE}/{exploration.id}/input_ports/{input_port.dataset.id}",
        )
        assert response.status_code == 403, response.text

    def test_delete_exploration(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        exploration = ExplorationFactory(owner=user)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__CREATE_EXPLORATION],
        )
        GlobalRoleAssignmentFactory(user_id=user.id, role_id=role.id)
        response = client.delete(f"{ROUTE}/{exploration.id}")
        assert response.status_code == 200, response.text

    def test_delete_exploration_not_owner_returns_403(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        other_user = UserFactory()
        exploration = ExplorationFactory(owner=other_user)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__CREATE_EXPLORATION],
        )
        GlobalRoleAssignmentFactory(user_id=user.id, role_id=role.id)
        response = client.delete(f"{ROUTE}/{exploration.id}")
        assert response.status_code == 403, response.text

    def test_delete_exploration_with_finalizers_returns_202(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        exploration = ExplorationFactory(owner=user, finalizers=["some-system"])
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__CREATE_EXPLORATION],
        )
        GlobalRoleAssignmentFactory(user_id=user.id, role_id=role.id)
        response = client.delete(f"{ROUTE}/{exploration.id}")
        assert response.status_code == 202, response.text

    def test_add_finalizer_to_exploration(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        exploration = ExplorationFactory(owner=user)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__CREATE_EXPLORATION],
        )
        GlobalRoleAssignmentFactory(user_id=user.id, role_id=role.id)
        response = client.post(
            f"{ROUTE}/{exploration.id}/finalizers",
            json={"finalizer": "my-system"},
        )
        assert response.status_code == 200, response.text

    def test_add_finalizer_to_exploration_not_owner(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        other_user = UserFactory()
        exploration = ExplorationFactory(owner=other_user)
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__CREATE_EXPLORATION],
        )
        GlobalRoleAssignmentFactory(user_id=user.id, role_id=role.id)
        response = client.post(
            f"{ROUTE}/{exploration.id}/finalizers",
            json={"finalizer": "my-system"},
        )
        assert response.status_code == 403, response.text

    def test_remove_finalizer_from_exploration_triggers_deletion(self, client):
        """Removing the last finalizer from a DELETING exploration deletes it."""
        from app.data_products.status import AbstractDataProductStatus

        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        exploration = ExplorationFactory(
            owner=user,
            finalizers=["last-one"],
            status=AbstractDataProductStatus.DELETING.value,
        )
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__CREATE_EXPLORATION],
        )
        GlobalRoleAssignmentFactory(user_id=user.id, role_id=role.id)
        response = client.delete(f"{ROUTE}/{exploration.id}/finalizers/last-one")
        assert response.status_code == 200, response.text
        assert client.get(f"{ROUTE}/{exploration.id}").status_code == 404

    def test_remove_finalizer_from_exploration_not_last(self, client):
        """Removing a non-last finalizer keeps the exploration alive."""
        from app.data_products.status import AbstractDataProductStatus

        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        exploration = ExplorationFactory(
            owner=user,
            finalizers=["a", "b"],
            status=AbstractDataProductStatus.DELETING.value,
        )
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__CREATE_EXPLORATION],
        )
        GlobalRoleAssignmentFactory(user_id=user.id, role_id=role.id)
        response = client.delete(f"{ROUTE}/{exploration.id}/finalizers/a")
        assert response.status_code == 200, response.text
        assert client.get(f"{ROUTE}/{exploration.id}").status_code == 200

    def test_remove_finalizer_from_exploration_not_owner(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        other_user = UserFactory()
        exploration = ExplorationFactory(owner=other_user, finalizers=["my-system"])
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__CREATE_EXPLORATION],
        )
        GlobalRoleAssignmentFactory(user_id=user.id, role_id=role.id)
        response = client.delete(f"{ROUTE}/{exploration.id}/finalizers/my-system")
        assert response.status_code == 403, response.text
