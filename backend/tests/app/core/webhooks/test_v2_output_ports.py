from contextlib import contextmanager
from unittest.mock import AsyncMock, patch

import pytest

from app.authorization.roles.schema import Scope
from app.authorization.roles.service import RoleService
from app.core.authz import Action
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    DataProductSettingFactory,
    DatasetFactory,
    GlobalRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

DP_ENDPOINT = "/api/v2/data_products"


@contextmanager
def webhook_v2_config():
    original = settings.WEBHOOK_V2_URL
    settings.WEBHOOK_V2_URL = "http://test-v2.example.com/hook"
    try:
        yield
    finally:
        settings.WEBHOOK_V2_URL = original


@pytest.fixture
def output_port_payload():
    user = UserFactory()
    return {
        "name": "Test Output Port",
        "description": "Test Description",
        "namespace": "test-op-namespace",
        "tag_ids": [],
        "owners": [str(user.id)],
        "access_type": "restricted",
    }


class TestOutputPortV2Events:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def _setup_admin(self, session):
        RoleService(db=session).initialize_prototype_roles()
        from app.settings import settings as s

        user = UserFactory(external_id=s.DEFAULT_USERNAME)
        role = RoleFactory(scope=Scope.GLOBAL, permissions=list(Action))
        GlobalRoleAssignmentFactory(user_id=user.id, role_id=role.id)
        return user

    def _op_endpoint(self, dp_id):
        return f"{DP_ENDPOINT}/{dp_id}/output_ports"

    # --- output_port.created ---

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_created_fires_event(
        self, mock_webhook, client, session, output_port_payload
    ):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)
        dp = DataProductFactory()

        with webhook_v2_config():
            response = client.post(self._op_endpoint(dp.id), json=output_port_payload)

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "output_port.created"
        assert "data_product" in data
        assert "output_port" in data

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_created_does_not_fire_on_failure(self, mock_webhook, client, session):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)

        with webhook_v2_config():
            response = client.post(
                self._op_endpoint(self.invalid_id), json={"invalid": "payload"}
            )

        assert response.status_code != 200
        mock_webhook.assert_not_awaited()

    # --- output_port.updated ---

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_updated_fires_event(
        self, mock_webhook, client, session, output_port_payload
    ):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)
        dp = DataProductFactory()
        op = DatasetFactory(data_product=dp)

        with webhook_v2_config():
            response = client.put(
                f"{self._op_endpoint(dp.id)}/{op.id}", json=output_port_payload
            )

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "output_port.updated"
        assert "data_product" in data
        assert "output_port" in data

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_updated_does_not_fire_on_failure(
        self, mock_webhook, client, session, output_port_payload
    ):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)

        with webhook_v2_config():
            response = client.put(
                f"{self._op_endpoint(self.invalid_id)}/{self.invalid_id}",
                json=output_port_payload,
            )

        assert response.status_code != 200
        mock_webhook.assert_not_awaited()

    # --- output_port.deleted ---

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_deleted_fires_event(self, mock_webhook, client, session):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)
        dp = DataProductFactory()
        op = DatasetFactory(data_product=dp)

        with webhook_v2_config():
            response = client.delete(f"{self._op_endpoint(dp.id)}/{op.id}")

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "output_port.deleted"
        assert "data_product" in data
        assert "output_port" in data

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_deleted_does_not_fire_on_failure(self, mock_webhook, client, session):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)

        with webhook_v2_config():
            response = client.delete(
                f"{self._op_endpoint(self.invalid_id)}/{self.invalid_id}"
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()

    # --- output_port.about_updated ---

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_about_updated_fires_event(self, mock_webhook, client, session):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)
        dp = DataProductFactory()
        op = DatasetFactory(data_product=dp)

        with webhook_v2_config():
            response = client.put(
                f"{self._op_endpoint(dp.id)}/{op.id}/about",
                json={"about": "new text"},
            )

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "output_port.about_updated"
        assert "data_product" in data
        assert "output_port" in data

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_about_updated_does_not_fire_on_failure(
        self, mock_webhook, client, session
    ):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)

        with webhook_v2_config():
            response = client.put(
                f"{self._op_endpoint(self.invalid_id)}/{self.invalid_id}/about",
                json={"about": "text"},
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()

    # --- output_port.status_updated ---

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_status_updated_fires_event(self, mock_webhook, client, session):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)
        dp = DataProductFactory()
        op = DatasetFactory(data_product=dp)

        with webhook_v2_config():
            response = client.put(
                f"{self._op_endpoint(dp.id)}/{op.id}/status",
                json={"status": "active"},
            )

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "output_port.status_updated"
        assert "data_product" in data
        assert "output_port" in data

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_status_updated_does_not_fire_on_failure(
        self, mock_webhook, client, session
    ):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)

        with webhook_v2_config():
            response = client.put(
                f"{self._op_endpoint(self.invalid_id)}/{self.invalid_id}/status",
                json={"status": "active"},
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()

    # --- output_port.setting_changed ---

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_setting_changed_fires_event(self, mock_webhook, client, session):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)
        dp = DataProductFactory()
        op = DatasetFactory(data_product=dp)
        setting = DataProductSettingFactory(scope="dataset")

        with webhook_v2_config():
            response = client.post(
                f"{self._op_endpoint(dp.id)}/{op.id}/settings/{setting.id}",
                params={"value": "test-value"},
            )

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "output_port.setting_changed"
        assert "data_product" in data
        assert "output_port" in data

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_setting_changed_does_not_fire_on_failure(
        self, mock_webhook, client, session
    ):
        # No admin — 403 avoids triggering unhandled exceptions in settings service
        mock_webhook.return_value = AsyncMock()
        dp = DataProductFactory()
        op = DatasetFactory(data_product=dp)
        setting = DataProductSettingFactory()

        with webhook_v2_config():
            response = client.post(
                f"{self._op_endpoint(dp.id)}/{op.id}/settings/{setting.id}",
                params={"value": "test-value"},
            )

        assert response.status_code == 403
        mock_webhook.assert_not_awaited()

    # --- output_port.link_approved ---

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_link_approved_fires_event(self, mock_webhook, client, session):
        from app.authorization.role_assignments.enums import DecisionStatus
        from tests.factories import DataProductDatasetAssociationFactory

        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)
        dp = DataProductFactory()
        op = DatasetFactory(data_product=dp)
        consumer_dp = DataProductFactory()
        DataProductDatasetAssociationFactory(
            data_product=consumer_dp, dataset=op, status=DecisionStatus.PENDING
        )

        with webhook_v2_config():
            response = client.post(
                f"{self._op_endpoint(dp.id)}/{op.id}/input_ports/approve",
                json={"consuming_data_product_id": str(consumer_dp.id)},
            )

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "output_port.link_approved"
        assert "data_product" in data
        assert "output_port" in data

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_link_approved_does_not_fire_on_failure(
        self, mock_webhook, client, session
    ):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)

        with webhook_v2_config():
            response = client.post(
                f"{self._op_endpoint(self.invalid_id)}/{self.invalid_id}/input_ports/approve",
                json={"consuming_data_product_id": self.invalid_id},
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()
