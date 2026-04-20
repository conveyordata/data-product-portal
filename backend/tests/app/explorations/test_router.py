import uuid

import faker

from app.authorization.roles.schema import Scope
from app.core.authz import Action
from app.settings import settings
from tests.factories import (
    DomainFactory,
    GlobalRoleAssignmentFactory,
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

    def test_get_explorations(self, client):
        exploration = ExplorationFactory()
        response = client.get(ROUTE)
        assert response.status_code == 200, response.text
        assert len(response.json()["explorations"]) == 1
        assert response.json()["explorations"][0]["id"] == str(exploration.id)
