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


class TestGetDataProductAnalyticsInputPorts:
    def test_input_ports_included_in_analytics(self):
        mock_db = MagicMock()
        mock_token = MagicMock()
        mock_token.token = "test-token"
        mock_user = {
            "id": UUID("dddddddd-0000-0000-0000-000000000001"),
            "email": "u@e.com",
        }

        # Mock data product
        mock_dp = MagicMock()
        mock_dp.id = UUID(DATA_PRODUCT_ID)
        mock_dp.name = "Marketing Customer 360"
        mock_dp.namespace = "marketing_customer_360"
        mock_dp.description = "desc"
        mock_dp.about = None
        mock_dp.usage = None
        mock_dp.status = "active"
        mock_dp.owner_email = "owner@example.com"
        mock_dp.created_at = datetime(2024, 1, 1)
        mock_dp.updated_at = datetime(2024, 1, 1)
        mock_dp.tags = []
        mock_dp.domain = MagicMock()
        mock_dp.domain.name = "Marketing"
        mock_dp.domain.id = UUID("00000000-0000-0000-0000-000000000001")
        mock_dp.domain.description = "Marketing domain"
        mock_dp.lifecycle = None
        mock_dp.type = MagicMock()
        mock_dp.type.id = UUID("11111111-0000-0000-0000-000000000001")
        mock_dp.type.name = "Analytics"
        mock_dp.type.description = "Analytics type"
        mock_dp.type.icon_key = "analytics"
        mock_dp.data_product_settings = []

        # Mock input port (what Marketing Customer 360 consumes from another output port)
        mock_ip = MagicMock()
        mock_ip.dataset_id = UUID(OUTPUT_PORT_ID)
        mock_ip.dataset = MagicMock()
        mock_ip.dataset.name = "Raw Events"
        mock_ip.dataset.data_product_id = UUID("eeeeeeee-0000-0000-0000-000000000001")
        mock_ip.dataset.data_product = MagicMock()
        mock_ip.dataset.data_product.name = "Events Platform"
        mock_ip.status = DecisionStatus.APPROVED
        mock_ip.justification = "Need raw events for modeling"
        mock_ip.requested_by = MagicMock()
        mock_ip.requested_by.email = "analyst@example.com"
        mock_ip.requested_on = datetime(2024, 2, 15)
        mock_ip.approved_on = datetime(2024, 2, 20)
        mock_ip.denied_on = None

        mock_dp_service = MagicMock()
        mock_dp_service.get_data_product.return_value = mock_dp

        mock_op_service = MagicMock()
        mock_op_service.get_output_ports.return_value = []

        mock_do_service = MagicMock()
        mock_do_service.get_data_outputs.return_value = []

        # db.scalars(...).unique().all() returns the input port records
        mock_db.scalars.return_value.unique.return_value.all.return_value = [mock_ip]

        with (
            patch("app.mcp.mcp.get_db_session", return_value=iter([mock_db])),
            patch("app.mcp.mcp.get_access_token", return_value=mock_token),
            patch("app.mcp.mcp.get_mcp_authenticated_user", return_value=mock_user),
            patch("app.mcp.mcp.DataProductService", return_value=mock_dp_service),
            patch("app.mcp.mcp.OutputPortService", return_value=mock_op_service),
            patch("app.mcp.mcp.DataOutputService", return_value=mock_do_service),
        ):
            from app.mcp.mcp import get_data_product_analytics

            result = get_data_product_analytics(data_product_id=DATA_PRODUCT_ID)

        assert "analytics" in result
        assert "input_ports" in result["analytics"]
        ports = result["analytics"]["input_ports"]
        assert len(ports) == 1
        assert ports[0]["output_port_id"] == OUTPUT_PORT_ID
        assert ports[0]["output_port_name"] == "Raw Events"
        assert (
            ports[0]["producing_data_product_id"]
            == "eeeeeeee-0000-0000-0000-000000000001"
        )
        assert ports[0]["producing_data_product_name"] == "Events Platform"
        assert ports[0]["status"] == DecisionStatus.APPROVED.value
        assert ports[0]["justification"] == "Need raw events for modeling"
        assert ports[0]["requested_by_email"] == "analyst@example.com"
        assert ports[0]["requested_on"] == "2024-02-15T00:00:00"
        assert ports[0]["approved_on"] == "2024-02-20T00:00:00"
        assert ports[0]["denied_on"] is None

    def test_input_ports_empty_when_none(self):
        mock_db = MagicMock()
        mock_token = MagicMock()
        mock_token.token = "test-token"
        mock_user = {
            "id": UUID("dddddddd-0000-0000-0000-000000000001"),
            "email": "u@e.com",
        }

        mock_dp = MagicMock()
        mock_dp.id = UUID(DATA_PRODUCT_ID)
        mock_dp.name = "Marketing Customer 360"
        mock_dp.namespace = "marketing_customer_360"
        mock_dp.description = "desc"
        mock_dp.about = None
        mock_dp.usage = None
        mock_dp.status = "active"
        mock_dp.owner_email = "owner@example.com"
        mock_dp.created_at = datetime(2024, 1, 1)
        mock_dp.updated_at = datetime(2024, 1, 1)
        mock_dp.tags = []
        mock_dp.domain = MagicMock()
        mock_dp.domain.name = "Marketing"
        mock_dp.domain.id = UUID("00000000-0000-0000-0000-000000000001")
        mock_dp.domain.description = "Marketing domain"
        mock_dp.lifecycle = None
        mock_dp.type = MagicMock()
        mock_dp.type.id = UUID("11111111-0000-0000-0000-000000000001")
        mock_dp.type.name = "Analytics"
        mock_dp.type.description = "Analytics type"
        mock_dp.type.icon_key = "analytics"
        mock_dp.data_product_settings = []

        mock_dp_service = MagicMock()
        mock_dp_service.get_data_product.return_value = mock_dp

        mock_op_service = MagicMock()
        mock_op_service.get_output_ports.return_value = []

        mock_do_service = MagicMock()
        mock_do_service.get_data_outputs.return_value = []

        mock_db.scalars.return_value.unique.return_value.all.return_value = []

        with (
            patch("app.mcp.mcp.get_db_session", return_value=iter([mock_db])),
            patch("app.mcp.mcp.get_access_token", return_value=mock_token),
            patch("app.mcp.mcp.get_mcp_authenticated_user", return_value=mock_user),
            patch("app.mcp.mcp.DataProductService", return_value=mock_dp_service),
            patch("app.mcp.mcp.OutputPortService", return_value=mock_op_service),
            patch("app.mcp.mcp.DataOutputService", return_value=mock_do_service),
        ):
            from app.mcp.mcp import get_data_product_analytics

            result = get_data_product_analytics(data_product_id=DATA_PRODUCT_ID)

        assert result["analytics"]["input_ports"] == []
