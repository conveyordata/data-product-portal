import uuid

import faker

from tests.factories import DomainFactory
from tests.factories.exploration import ExplorationFactory

ROUTE = "/api/v2/explorations"


class TestExplorationRouter:
    def test_create_exploration(self, client):
        d = DomainFactory()
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
        e = ExplorationFactory()
        response = client.get(ROUTE)
        assert response.status_code == 200, response.text
        assert len(response.json()["explorations"]) == 1
        assert response.json()["explorations"][0]["id"] == str(e.id)
