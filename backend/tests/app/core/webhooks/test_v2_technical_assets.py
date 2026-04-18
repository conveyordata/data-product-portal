from contextlib import contextmanager
from unittest.mock import AsyncMock, patch

from app.authorization.roles.schema import Scope
from app.authorization.roles.service import RoleService
from app.core.authz import Action
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    GlobalRoleAssignmentFactory,
    PlatformServiceFactory,
    RoleFactory,
    TagFactory,
    TechnicalAssetFactory,
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


class TestTechnicalAssetV2Events:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def _setup_admin(self, session):
        RoleService(db=session).initialize_prototype_roles()
        from app.settings import settings as s

        user = UserFactory(external_id=s.DEFAULT_USERNAME)
        role = RoleFactory(scope=Scope.GLOBAL, permissions=list(Action))
        GlobalRoleAssignmentFactory(user_id=user.id, role_id=role.id)
        return user

    def _ta_endpoint(self, dp_id):
        return f"{DP_ENDPOINT}/{dp_id}/technical_assets"

    def _create_payload(self):
        service = PlatformServiceFactory()
        tag = TagFactory()
        return {
            "name": "Test Asset",
            "description": "desc",
            "namespace": "test-namespace",
            "technical_mapping": "default",
            "configuration": {
                "bucket": "test",
                "path": "test",
                "configuration_type": "S3TechnicalAssetConfiguration",
            },
            "platform_id": str(service.platform.id),
            "service_id": str(service.id),
            "tag_ids": [str(tag.id)],
        }

    # --- technical_asset.created ---

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_created_fires_event(self, mock_webhook, client, session):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)
        dp = DataProductFactory()

        with webhook_v2_config():
            response = client.post(
                self._ta_endpoint(dp.id),
                json=self._create_payload(),
            )

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "technical_asset.created"
        assert "data_product" in data
        assert "technical_asset" in data

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_created_does_not_fire_on_failure(self, mock_webhook, client, session):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)

        with webhook_v2_config():
            response = client.post(
                self._ta_endpoint(self.invalid_id), json={"invalid": "payload"}
            )

        assert response.status_code != 200
        mock_webhook.assert_not_awaited()

    # --- technical_asset.updated ---

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_updated_fires_event(self, mock_webhook, client, session):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)
        dp = DataProductFactory()
        ta = TechnicalAssetFactory(owner=dp)
        tag = TagFactory()

        with webhook_v2_config():
            response = client.put(
                f"{self._ta_endpoint(dp.id)}/{ta.id}",
                json={
                    "name": "Updated",
                    "description": "desc",
                    "tag_ids": [str(tag.id)],
                },
            )

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "technical_asset.updated"
        assert "data_product" in data
        assert "technical_asset" in data

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_updated_does_not_fire_on_failure(self, mock_webhook, client, session):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)

        with webhook_v2_config():
            response = client.put(
                f"{self._ta_endpoint(self.invalid_id)}/{self.invalid_id}",
                json={"name": "Updated", "description": "desc", "tag_ids": []},
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()

    # --- technical_asset.deleted ---

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_deleted_fires_event(self, mock_webhook, client, session):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)
        dp = DataProductFactory()
        ta = TechnicalAssetFactory(owner=dp)

        with webhook_v2_config():
            response = client.delete(f"{self._ta_endpoint(dp.id)}/{ta.id}")

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "technical_asset.deleted"
        assert "data_product" in data
        assert "technical_asset" in data

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_deleted_does_not_fire_on_failure(self, mock_webhook, client, session):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)

        with webhook_v2_config():
            response = client.delete(
                f"{self._ta_endpoint(self.invalid_id)}/{self.invalid_id}"
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()

    def _link_endpoint(self, dp_id, op_id):
        return f"{DP_ENDPOINT}/{dp_id}/output_ports/{op_id}/technical_assets"

    # --- technical_asset.linked ---

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_linked_fires_event(self, mock_webhook, client, session):
        from tests.factories import DatasetFactory

        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)
        dp = DataProductFactory()
        op = DatasetFactory(data_product=dp)
        ta = TechnicalAssetFactory(owner=dp)

        with webhook_v2_config():
            response = client.post(
                f"{self._link_endpoint(dp.id, op.id)}/add",
                json={"technical_asset_id": str(ta.id)},
            )

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "technical_asset.linked"
        assert "data_product" in data
        assert "technical_asset" in data

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_linked_does_not_fire_on_failure(self, mock_webhook, client, session):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)

        with webhook_v2_config():
            response = client.post(
                f"{self._link_endpoint(self.invalid_id, self.invalid_id)}/add",
                json={"technical_asset_id": self.invalid_id},
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()

    # --- technical_asset.link_approved ---

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_link_approved_fires_event(self, mock_webhook, client, session):
        from app.authorization.role_assignments.enums import DecisionStatus
        from tests.factories import DataOutputDatasetAssociationFactory, DatasetFactory

        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)
        dp = DataProductFactory()
        op = DatasetFactory(data_product=dp)
        ta = TechnicalAssetFactory(owner=dp)
        DataOutputDatasetAssociationFactory(
            data_output=ta, dataset=op, status=DecisionStatus.PENDING
        )

        with webhook_v2_config():
            response = client.post(
                f"{self._link_endpoint(dp.id, op.id)}/approve_link_request",
                json={"technical_asset_id": str(ta.id)},
            )

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "technical_asset.link_approved"
        assert "data_product" in data
        assert "technical_asset" in data

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_link_approved_does_not_fire_on_failure(
        self, mock_webhook, client, session
    ):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)

        with webhook_v2_config():
            response = client.post(
                f"{self._link_endpoint(self.invalid_id, self.invalid_id)}/approve_link_request",
                json={"technical_asset_id": self.invalid_id},
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()

    # --- technical_asset.link_denied ---

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_link_denied_fires_event(self, mock_webhook, client, session):
        from app.authorization.role_assignments.enums import DecisionStatus
        from tests.factories import DataOutputDatasetAssociationFactory, DatasetFactory

        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)
        dp = DataProductFactory()
        op = DatasetFactory(data_product=dp)
        ta = TechnicalAssetFactory(owner=dp)
        DataOutputDatasetAssociationFactory(
            data_output=ta, dataset=op, status=DecisionStatus.PENDING
        )

        with webhook_v2_config():
            response = client.post(
                f"{self._link_endpoint(dp.id, op.id)}/deny_link_request",
                json={"technical_asset_id": str(ta.id)},
            )

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "technical_asset.link_denied"
        assert "data_product" in data
        assert "technical_asset" in data

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_link_denied_does_not_fire_on_failure(self, mock_webhook, client, session):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)

        with webhook_v2_config():
            response = client.post(
                f"{self._link_endpoint(self.invalid_id, self.invalid_id)}/deny_link_request",
                json={"technical_asset_id": self.invalid_id},
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()

    # --- technical_asset.unlinked ---

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_unlinked_fires_event(self, mock_webhook, client, session):
        from tests.factories import DataOutputDatasetAssociationFactory, DatasetFactory

        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)
        dp = DataProductFactory()
        op = DatasetFactory(data_product=dp)
        ta = TechnicalAssetFactory(owner=dp)
        DataOutputDatasetAssociationFactory(data_output=ta, dataset=op)

        with webhook_v2_config():
            response = client.request(
                method="DELETE",
                url=f"{self._link_endpoint(dp.id, op.id)}/remove",
                json={"technical_asset_id": str(ta.id)},
            )

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "technical_asset.unlinked"
        assert "data_product" in data
        assert "technical_asset" in data

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_unlinked_does_not_fire_on_failure(self, mock_webhook, client, session):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)

        with webhook_v2_config():
            response = client.request(
                method="DELETE",
                url=f"{self._link_endpoint(self.invalid_id, self.invalid_id)}/remove",
                json={"technical_asset_id": self.invalid_id},
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()

    # --- technical_asset.status_updated ---

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_status_updated_fires_event(self, mock_webhook, client, session):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)
        dp = DataProductFactory()
        ta = TechnicalAssetFactory(owner=dp)

        with webhook_v2_config():
            response = client.put(
                f"{self._ta_endpoint(dp.id)}/{ta.id}/status",
                json={"status": "active"},
            )

        assert response.status_code == 200
        mock_webhook.assert_awaited_once()
        event_type, data = mock_webhook.call_args.args
        assert event_type == "technical_asset.status_updated"
        assert "data_product" in data
        assert "technical_asset" in data

    @patch("app.core.webhooks.v2.call_v2_webhook")
    def test_status_updated_does_not_fire_on_failure(
        self, mock_webhook, client, session
    ):
        mock_webhook.return_value = AsyncMock()
        self._setup_admin(session)

        with webhook_v2_config():
            response = client.put(
                f"{self._ta_endpoint(self.invalid_id)}/{self.invalid_id}/status",
                json={"status": "active"},
            )

        assert response.status_code == 404
        mock_webhook.assert_not_awaited()
