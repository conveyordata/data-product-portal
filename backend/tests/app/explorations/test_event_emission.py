"""Integration tests: exploration REST endpoints emit ORM-tracked events."""

import uuid
from unittest.mock import AsyncMock, patch

import faker

from app.authorization.roles.schema import Scope
from app.core.authz import Action
from app.settings import settings
from tests.app.core.webhooks.helpers import webhook_v2_config
from tests.factories import (
    DomainFactory,
    GlobalRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

ROUTE = "/api/v2/explorations"


def _create_payload(domain_id: str) -> dict:
    return {
        "name": str(uuid.uuid4()),
        "namespace": str(uuid.uuid4()),
        "domain_id": domain_id,
        "description": faker.Faker().text(),
    }


def _authorized_user():
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    role = RoleFactory(
        scope=Scope.GLOBAL, permissions=[Action.GLOBAL__CREATE_EXPLORATION]
    )
    GlobalRoleAssignmentFactory(user_id=user.id, role_id=role.id)
    return user


class TestExplorationEventEmission:
    @patch("app.main.call_v2_webhook", new_callable=AsyncMock)
    def test_create_exploration_emits_created_event(self, mock_webhook, client):
        d = DomainFactory()
        _authorized_user()

        with webhook_v2_config():
            response = client.post(ROUTE, json=_create_payload(str(d.id)))

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, payload = mock_webhook.call_args.args
        assert event_type == "exploration.created"
        assert "id" in payload

    @patch("app.main.call_v2_webhook", new_callable=AsyncMock)
    def test_no_event_emitted_when_webhook_not_configured(self, mock_webhook, client):
        d = DomainFactory()
        _authorized_user()

        with webhook_v2_config(url=None):
            response = client.post(ROUTE, json=_create_payload(str(d.id)))

        assert response.status_code == 200
        mock_webhook.assert_not_awaited()

    @patch("app.main.call_v2_webhook", new_callable=AsyncMock)
    def test_no_event_emitted_on_failed_request(self, mock_webhook, client):
        """A 4xx response must not emit any event."""
        d = DomainFactory()
        # no authorized user → 403

        with webhook_v2_config():
            response = client.post(ROUTE, json=_create_payload(str(d.id)))

        assert response.status_code >= 400
        mock_webhook.assert_not_awaited()
