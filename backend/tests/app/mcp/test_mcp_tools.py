from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import UUID

from app.authorization.role_assignments.enums import DecisionStatus


def _make_mock_dataset(output_port_id: str, data_product_id: str):
    """Return a minimal mock Dataset that satisfies GetOutputPortResponse.model_validate."""
    ds = MagicMock()
    ds.id = UUID(output_port_id)
    ds.namespace = "test_namespace"
    ds.name = "Test Output Port"
    ds.description = "desc"
    ds.status = "active"
    ds.usage = None
    ds.about = None
    ds.access_type = "public"
    ds.data_product_id = UUID(data_product_id)
    ds.data_product_name = "Test DP"
    ds.owner_email = "owner@example.com"
    ds.created_at = datetime(2024, 1, 1)
    ds.updated_at = datetime(2024, 1, 1)
    ds.freshness_status = "fresh"
    ds.freshness_deadline_time = None
    ds.latest_freshness_at = None
    # Fields required by GetOutputPortResponse — extend as needed if validation fails
    ds.tags = []
    ds.rolled_up_tags = []
    ds.domain = MagicMock()
    ds.domain.id = UUID("00000000-0000-0000-0000-000000000001")
    ds.domain.name = "Finance"
    ds.domain.description = "Finance domain"
    ds.lifecycle = None
    ds.table_schema = None
    ds.quality_summary = None
    ds.semantic_model = None
    ds.curated_queries = []
    ds.data_product_settings = []
    ds.data_output_links = []
    ds.data_product = MagicMock()
    ds.data_product.name = "Test DP"
    ds.data_product.id = UUID(data_product_id)
    ds.data_product.icon_key = None
    ds.data_product.type = MagicMock()
    ds.data_product.type.icon_key = None
    return ds


def _make_mock_input_port(
    consuming_dp_id: str,
    consuming_dp_name: str,
    status: DecisionStatus,
    justification: str,
):
    ip = MagicMock()
    ip.consuming_abstract_data_product_id = UUID(consuming_dp_id)
    ip.consuming_abstract_data_product = MagicMock()
    ip.consuming_abstract_data_product.name = consuming_dp_name
    ip.status = status
    ip.justification = justification
    ip.requested_by = MagicMock()
    ip.requested_by.email = "requester@example.com"
    ip.approved_by = None
    ip.denied_by = None
    ip.requested_on = datetime(2024, 3, 1)
    ip.approved_on = None
    ip.denied_on = None
    return ip


OUTPUT_PORT_ID = "aaaaaaaa-0000-0000-0000-000000000001"
DATA_PRODUCT_ID = "bbbbbbbb-0000-0000-0000-000000000001"
CONSUMING_DP_ID = "cccccccc-0000-0000-0000-000000000001"


class TestGetOutputPortDetailsConsumingDataProducts:
    def test_consuming_data_products_included_in_response(self):
        mock_db = MagicMock()
        mock_token = MagicMock()
        mock_token.token = "test-token"
        mock_user = {
            "id": UUID("dddddddd-0000-0000-0000-000000000001"),
            "email": "u@e.com",
        }

        mock_dataset = _make_mock_dataset(OUTPUT_PORT_ID, DATA_PRODUCT_ID)
        mock_ip = _make_mock_input_port(
            CONSUMING_DP_ID,
            "Marketing Analytics",
            DecisionStatus.APPROVED,
            "Need it for reports",
        )

        mock_service = MagicMock()
        mock_service.get_dataset.return_value = mock_dataset
        mock_service.get_consuming_data_products.return_value = [mock_ip]

        with (
            patch("app.mcp.mcp.get_db_session", return_value=iter([mock_db])),
            patch("app.mcp.mcp.get_access_token", return_value=mock_token),
            patch("app.mcp.mcp.get_mcp_authenticated_user", return_value=mock_user),
            patch("app.mcp.mcp.OutputPortService", return_value=mock_service),
        ):
            from app.mcp.mcp import get_output_port_details

            result = get_output_port_details(output_port_id=OUTPUT_PORT_ID)

        assert "consuming_data_products" in result
        grants = result["consuming_data_products"]
        assert len(grants) == 1
        assert grants[0]["consuming_data_product_id"] == CONSUMING_DP_ID
        assert grants[0]["consuming_data_product_name"] == "Marketing Analytics"
        assert grants[0]["status"] == DecisionStatus.APPROVED.value
        assert grants[0]["justification"] == "Need it for reports"
        assert grants[0]["requested_by_email"] == "requester@example.com"
        assert grants[0]["approved_by_email"] is None
        assert grants[0]["denied_by_email"] is None
        assert grants[0]["requested_on"] == "2024-03-01T00:00:00"
        assert grants[0]["approved_on"] is None
        assert grants[0]["denied_on"] is None

    def test_consuming_data_products_empty_when_none(self):
        mock_db = MagicMock()
        mock_token = MagicMock()
        mock_token.token = "test-token"
        mock_user = {
            "id": UUID("dddddddd-0000-0000-0000-000000000001"),
            "email": "u@e.com",
        }

        mock_dataset = _make_mock_dataset(OUTPUT_PORT_ID, DATA_PRODUCT_ID)
        mock_service = MagicMock()
        mock_service.get_dataset.return_value = mock_dataset
        mock_service.get_consuming_data_products.return_value = []

        with (
            patch("app.mcp.mcp.get_db_session", return_value=iter([mock_db])),
            patch("app.mcp.mcp.get_access_token", return_value=mock_token),
            patch("app.mcp.mcp.get_mcp_authenticated_user", return_value=mock_user),
            patch("app.mcp.mcp.OutputPortService", return_value=mock_service),
        ):
            from app.mcp.mcp import get_output_port_details

            result = get_output_port_details(output_port_id=OUTPUT_PORT_ID)

        assert result["consuming_data_products"] == []
