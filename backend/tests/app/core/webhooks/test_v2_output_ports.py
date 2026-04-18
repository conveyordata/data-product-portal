from unittest.mock import AsyncMock, patch

import pytest

from tests.app.core.webhooks.helpers import webhook_v2_config
from tests.factories import (
    DataProductFactory,
    DataProductSettingFactory,
    DatasetFactory,
    UserFactory,
)

DP_ENDPOINT = "/api/v2/data_products"


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

    def _op_endpoint(self, dp_id):
        return f"{DP_ENDPOINT}/{dp_id}/output_ports"

    # --- output_port.created ---

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_created_fires_event(self, mock_webhook, client, output_port_payload):
        mock_webhook.return_value = AsyncMock()
        dp = DataProductFactory()

        with webhook_v2_config():
            response = client.post(self._op_endpoint(dp.id), json=output_port_payload)

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "output_port.created"
        assert "data_product" in data
        assert "output_port" in data

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_created_does_not_fire_on_failure(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()

        with webhook_v2_config():
            response = client.post(
                self._op_endpoint(self.invalid_id), json={"invalid": "payload"}
            )

        assert response.status_code != 200
        mock_webhook.assert_not_awaited()

    # --- output_port.updated ---

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_updated_fires_event(self, mock_webhook, client, output_port_payload):
        mock_webhook.return_value = AsyncMock()
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

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_updated_does_not_fire_on_failure(
        self, mock_webhook, client, output_port_payload
    ):
        mock_webhook.return_value = AsyncMock()

        with webhook_v2_config():
            response = client.put(
                f"{self._op_endpoint(self.invalid_id)}/{self.invalid_id}",
                json=output_port_payload,
            )

        assert response.status_code != 200
        mock_webhook.assert_not_awaited()

    # --- output_port.deleted ---

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_deleted_fires_event(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()
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

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_deleted_does_not_fire_on_failure(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()

        with webhook_v2_config():
            response = client.delete(
                f"{self._op_endpoint(self.invalid_id)}/{self.invalid_id}"
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()

    # --- output_port.about_updated ---

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_about_updated_fires_event(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()
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

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_about_updated_does_not_fire_on_failure(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()

        with webhook_v2_config():
            response = client.put(
                f"{self._op_endpoint(self.invalid_id)}/{self.invalid_id}/about",
                json={"about": "text"},
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()

    # --- output_port.status_updated ---

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_status_updated_fires_event(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()
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

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_status_updated_does_not_fire_on_failure(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()

        with webhook_v2_config():
            response = client.put(
                f"{self._op_endpoint(self.invalid_id)}/{self.invalid_id}/status",
                json={"status": "active"},
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()

    # --- output_port.setting_changed ---

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_setting_changed_fires_event(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()
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
    def test_setting_changed_does_not_fire_on_failure(self, mock_webhook, client):
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

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_link_approved_fires_event(self, mock_webhook, client):
        from app.authorization.role_assignments.enums import DecisionStatus
        from tests.factories import DataProductDatasetAssociationFactory

        mock_webhook.return_value = AsyncMock()
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

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_link_approved_does_not_fire_on_failure(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()

        with webhook_v2_config():
            response = client.post(
                f"{self._op_endpoint(self.invalid_id)}/{self.invalid_id}/input_ports/approve",
                json={"consuming_data_product_id": self.invalid_id},
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()
