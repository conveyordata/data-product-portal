"""Integration tests: exploration REST endpoints emit ORM-tracked events."""

import uuid

import faker

from tests.conftest import webhook_v2_config
from tests.factories import DomainFactory

ROUTE = "/api/v2/explorations"


def _create_payload(domain_id: str) -> dict:
    return {
        "name": str(uuid.uuid4()),
        "namespace": str(uuid.uuid4()),
        "domain_id": domain_id,
        "description": faker.Faker().text(),
    }


class TestExplorationEventEmission:
    def test_create_exploration_emits_created_event(self, capture_events, client):
        response = client.post(ROUTE, json=_create_payload(str(DomainFactory().id)))

        assert response.status_code == 200
        assert len(capture_events.captured_events) == 1
        assert capture_events.captured_events[0].event_type() == "exploration.event"

    def test_no_event_emitted_when_webhook_not_configured(self, capture_events, client):
        with webhook_v2_config(url=None):
            response = client.post(ROUTE, json=_create_payload(str(DomainFactory().id)))

        assert response.status_code == 200
        assert len(capture_events.captured_events) == 0

    def test_no_event_emitted_on_failed_request(
        self, capture_events, client, everyone_role_permissions
    ):
        """A 4xx response must not emit any event."""

        with everyone_role_permissions(permissions=[]):
            response = client.post(ROUTE, json=_create_payload(str(uuid.uuid4())))

        assert response.status_code >= 400
        assert len(capture_events.captured_events) == 0
