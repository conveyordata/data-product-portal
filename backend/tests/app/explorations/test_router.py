import uuid

import faker

from app.authorization.roles.schema import Scope
from app.core.authz import Action
from app.settings import settings
from tests.factories import (
    DatasetFactory,
    DomainFactory,
    GlobalRoleAssignmentFactory,
    InputPortFactory,
    RoleFactory,
    UserFactory,
)
from tests.factories.exploration import ExplorationFactory

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
                    "output_ports": [str(DatasetFactory().id)],
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
                "output_ports": [str(DatasetFactory().id)],
                "justification": "I am your king!",
            },
        )
        assert response.status_code == 200, response.text
        assert len(response.json()["input_port_ids"]) == 1

    def test_request_input_ports_for_exploration_does_not_exist(self, client):
        response = client.post(
            f"{ROUTE}/{uuid.uuid4()}/input_ports",
            json={
                "output_ports": [str(DatasetFactory().id)],
                "justification": "I am your king!",
            },
        )
        assert response.status_code == 404, response.text

    def test_request_input_ports_for_exploration_not_owner(self, client):
        exploration = ExplorationFactory()
        response = client.post(
            f"{ROUTE}/{exploration.id}/input_ports",
            json={
                "output_ports": [str(DatasetFactory().id)],
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
