from unittest.mock import AsyncMock, patch

import pytest

from app.authorization.roles.schema import Scope
from tests.app.core.webhooks.helpers import webhook_v2_config
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DataProductSettingFactory,
    DataProductTypeFactory,
    DatasetFactory,
    DomainFactory,
    LifecycleFactory,
    RoleFactory,
    TagFactory,
    UserFactory,
)

ENDPOINT = "/api/v2/data_products"


@pytest.fixture
def create_payload():
    domain = DomainFactory()
    lifecycle = LifecycleFactory()
    dp_type = DataProductTypeFactory()
    user = UserFactory()
    tag = TagFactory()
    return {
        "name": "Test Data Product",
        "description": "Test Description",
        "namespace": "test-dp-namespace",
        "tag_ids": [str(tag.id)],
        "type_id": str(dp_type.id),
        "owners": [str(user.id)],
        "lifecycle_id": str(lifecycle.id),
        "domain_id": str(domain.id),
    }


@pytest.fixture
def update_payload():
    domain = DomainFactory()
    lifecycle = LifecycleFactory()
    dp_type = DataProductTypeFactory()
    user = UserFactory()
    return {
        "name": "Updated Name",
        "description": "Updated Description",
        "namespace": "updated-namespace",
        "tag_ids": [],
        "type_id": str(dp_type.id),
        "owners": [str(user.id)],
        "lifecycle_id": str(lifecycle.id),
        "domain_id": str(domain.id),
    }


class TestDataProductV2Events:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    # --- data_product.created ---

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_created_fires_event(self, mock_webhook, client, create_payload):
        mock_webhook.return_value = AsyncMock()

        with webhook_v2_config():
            response = client.post(ENDPOINT, json=create_payload)

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "data_product.created"
        assert "data_product" in data
        assert data["data_product"]["name"] == create_payload["name"]

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_created_does_not_fire_on_failure(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()

        with webhook_v2_config():
            response = client.post(ENDPOINT, json={"invalid": "payload"})

        assert response.status_code != 200
        mock_webhook.assert_not_awaited()

    # --- data_product.updated ---

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_updated_fires_event(self, mock_webhook, client, update_payload):
        mock_webhook.return_value = AsyncMock()
        dp = DataProductFactory()

        with webhook_v2_config():
            response = client.put(f"{ENDPOINT}/{dp.id}", json=update_payload)

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "data_product.updated"
        assert "data_product" in data

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_updated_does_not_fire_on_failure(
        self, mock_webhook, client, update_payload
    ):
        mock_webhook.return_value = AsyncMock()

        with webhook_v2_config():
            response = client.put(f"{ENDPOINT}/{self.invalid_id}", json=update_payload)

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()

    # --- data_product.deleted ---

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_deleted_fires_event(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()
        dp = DataProductFactory()

        with webhook_v2_config():
            response = client.delete(f"{ENDPOINT}/{dp.id}")

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "data_product.deleted"
        assert "data_product" in data

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_deleted_does_not_fire_on_failure(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()

        with webhook_v2_config():
            response = client.delete(f"{ENDPOINT}/{self.invalid_id}")

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()

    # --- data_product.about_updated ---

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_about_updated_fires_event(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()
        dp = DataProductFactory()

        with webhook_v2_config():
            response = client.put(
                f"{ENDPOINT}/{dp.id}/about",
                json={"about": "new about text"},
            )

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "data_product.about_updated"
        assert "data_product" in data

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_about_updated_does_not_fire_on_failure(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()

        with webhook_v2_config():
            response = client.put(
                f"{ENDPOINT}/{self.invalid_id}/about",
                json={"about": "text"},
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()

    # --- data_product.status_updated ---

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_status_updated_fires_event(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()
        dp = DataProductFactory()

        with webhook_v2_config():
            response = client.put(
                f"{ENDPOINT}/{dp.id}/status",
                json={"status": "active"},
            )

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "data_product.status_updated"
        assert "data_product" in data

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_status_updated_does_not_fire_on_failure(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()

        with webhook_v2_config():
            response = client.put(
                f"{ENDPOINT}/{self.invalid_id}/status",
                json={"status": "active"},
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()

    # --- data_product.setting_changed ---

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_setting_changed_fires_event(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()
        dp = DataProductFactory()
        setting = DataProductSettingFactory()

        with webhook_v2_config():
            response = client.post(
                f"{ENDPOINT}/{dp.id}/settings/{setting.id}",
                params={"value": "test-value"},
            )

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "data_product.setting_changed"
        assert "data_product" in data

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_setting_changed_does_not_fire_on_failure(self, mock_webhook, client):
        # No admin — user has no permissions, auth returns 403
        mock_webhook.return_value = AsyncMock()
        dp = DataProductFactory()
        setting = DataProductSettingFactory()

        with webhook_v2_config():
            response = client.post(
                f"{ENDPOINT}/{dp.id}/settings/{setting.id}",
                params={"value": "test-value"},
            )

        assert response.status_code == 403
        mock_webhook.assert_not_awaited()

    # --- data_product.input_port_linked ---

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_input_port_linked_fires_event(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()
        dp = DataProductFactory()
        output_port = DatasetFactory()

        with webhook_v2_config():
            response = client.post(
                f"{ENDPOINT}/{dp.id}/link_input_ports",
                json={"input_ports": [str(output_port.id)], "justification": "test"},
            )

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "data_product.input_port_linked"
        assert "data_product" in data

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_input_port_linked_does_not_fire_on_failure(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()

        with webhook_v2_config():
            response = client.post(
                f"{ENDPOINT}/{self.invalid_id}/link_input_ports",
                json={"input_ports": [self.invalid_id], "justification": "test"},
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()

    # --- data_product.input_port_unlinked ---

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_input_port_unlinked_fires_event(self, mock_webhook, client):
        from tests.factories import DataProductDatasetAssociationFactory

        mock_webhook.return_value = AsyncMock()
        dp = DataProductFactory()
        output_port = DatasetFactory()
        DataProductDatasetAssociationFactory(data_product=dp, dataset=output_port)

        with webhook_v2_config():
            response = client.delete(f"{ENDPOINT}/{dp.id}/input_ports/{output_port.id}")

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "data_product.input_port_unlinked"
        assert "data_product" in data

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_input_port_unlinked_does_not_fire_on_failure(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()

        with webhook_v2_config():
            response = client.delete(
                f"{ENDPOINT}/{self.invalid_id}/input_ports/{self.invalid_id}"
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()

    # --- data_product.team_member_added ---

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_team_member_added_fires_event(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()
        dp = DataProductFactory()
        member = UserFactory()
        role = RoleFactory(scope=Scope.DATA_PRODUCT, permissions=[])

        with webhook_v2_config():
            response = client.post(
                "/api/v2/authz/role_assignments/data_product",
                json={
                    "data_product_id": str(dp.id),
                    "user_id": str(member.id),
                    "role_id": str(role.id),
                },
            )

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "data_product.team_member_added"
        assert "data_product" in data

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_team_member_added_does_not_fire_on_failure(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()

        with webhook_v2_config():
            response = client.post(
                "/api/v2/authz/role_assignments/data_product",
                json={"invalid": "payload"},
            )

        assert response.status_code != 200
        mock_webhook.assert_not_awaited()

    # --- data_product.team_member_removed ---

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_team_member_removed_fires_event(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()
        dp = DataProductFactory()
        member = UserFactory()
        role = RoleFactory(scope=Scope.DATA_PRODUCT, permissions=[])
        assignment = DataProductRoleAssignmentFactory(
            data_product_id=dp.id, user_id=member.id, role_id=role.id
        )

        with webhook_v2_config():
            response = client.delete(
                f"/api/v2/authz/role_assignments/data_product/{assignment.id}"
            )

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "data_product.team_member_removed"
        assert "data_product" in data

    @pytest.mark.usefixtures("admin")
    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_team_member_removed_does_not_fire_on_failure(self, mock_webhook, client):
        mock_webhook.return_value = AsyncMock()

        with webhook_v2_config():
            response = client.delete(
                f"/api/v2/authz/role_assignments/data_product/{self.invalid_id}"
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()
