# ruff: noqa: S106
from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.mcp.mcp import get_data_product_usage  # type: ignore[attr-defined]

DATA_PRODUCT_ID = str(uuid4())
OUTPUT_PORT_ID_A = str(uuid4())
OUTPUT_PORT_ID_B = str(uuid4())
CONSUMER_ID_1 = str(uuid4())
CONSUMER_ID_2 = str(uuid4())


def _make_cost_row(output_port_id, name, compute, storage, overhead):
    row = MagicMock()
    row.output_port_id = output_port_id
    row.output_port_name = name
    row.compute_cost = Decimal(str(compute))
    row.storage_cost = Decimal(str(storage))
    row.platform_overhead_cost = Decimal(str(overhead))
    return row


def _make_stat(date_str, consumer_id, consumer_name, query_count):
    stat = MagicMock()
    stat.consumer_data_product_id = consumer_id
    stat.consumer_data_product_name = consumer_name
    stat.query_count = query_count
    return stat


def _make_output_port(port_id, name):
    op = MagicMock()
    op.id = port_id
    op.name = name
    return op


def _make_query_stats_response(stats):
    resp = MagicMock()
    resp.output_port_query_stats_responses = stats
    return resp


@patch("app.mcp.mcp.get_db_session")
@patch("app.mcp.mcp.get_access_token")
@patch("app.mcp.mcp.get_mcp_authenticated_user")
@patch("app.mcp.mcp.DataProductService")
@patch("app.mcp.mcp.OutputPortCostService")
@patch("app.mcp.mcp.OutputPortService")
@patch("app.mcp.mcp.OutputPortStatsService")
class TestGetDataProductUsage:
    def _setup_mocks(
        self,
        mock_stats_svc_cls,
        mock_output_port_svc_cls,
        mock_cost_svc_cls,
        mock_dp_svc_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
        cost_rows=None,
        output_ports=None,
        query_stats_by_port=None,
        data_product=None,
    ):
        mock_get_db.return_value = iter([MagicMock()])
        mock_get_token.return_value = MagicMock(token="tok")
        mock_get_user.return_value = {"id": str(uuid4())}

        dp = data_product or MagicMock()
        mock_dp_svc_cls.return_value.get_data_product.return_value = dp

        mock_cost_svc_cls.return_value.get_data_product_cost_summary.return_value = (
            cost_rows or []
        )
        mock_output_port_svc_cls.return_value.get_output_ports.return_value = (
            output_ports or []
        )

        def get_query_stats_side_effect(dataset_id, granularity, day_range):
            return (query_stats_by_port or {}).get(
                dataset_id, _make_query_stats_response([])
            )

        mock_stats_svc_cls.return_value.get_query_stats.side_effect = (
            get_query_stats_side_effect
        )

    def test_returns_cost_summary_for_single_output_port(
        self,
        mock_stats_svc_cls,
        mock_output_port_svc_cls,
        mock_cost_svc_cls,
        mock_dp_svc_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
    ):
        """Cost summary aggregates correctly for one output port."""
        cost_rows = [
            _make_cost_row(OUTPUT_PORT_ID_A, "Port A", "80.00", "40.00", "30.00")
        ]
        self._setup_mocks(
            mock_stats_svc_cls,
            mock_output_port_svc_cls,
            mock_cost_svc_cls,
            mock_dp_svc_cls,
            mock_get_user,
            mock_get_token,
            mock_get_db,
            cost_rows=cost_rows,
            output_ports=[],
        )

        result = get_data_product_usage(DATA_PRODUCT_ID)

        assert "error" not in result
        assert result["data_product_id"] == DATA_PRODUCT_ID
        assert result["day_range"] == 30
        cs = result["cost_summary"]
        assert cs["total_cost"] == 150.0
        assert len(cs["by_output_port"]) == 1
        port = cs["by_output_port"][0]
        assert port["output_port_id"] == str(OUTPUT_PORT_ID_A)
        assert port["output_port_name"] == "Port A"
        assert port["compute_cost"] == 80.0
        assert port["storage_cost"] == 40.0
        assert port["platform_overhead_cost"] == 30.0
        assert port["total_cost"] == 150.0

    def test_returns_cost_summary_for_multiple_output_ports(
        self,
        mock_stats_svc_cls,
        mock_output_port_svc_cls,
        mock_cost_svc_cls,
        mock_dp_svc_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
    ):
        """Total cost is sum across all output ports."""
        cost_rows = [
            _make_cost_row(OUTPUT_PORT_ID_A, "Port A", "80.00", "40.00", "30.00"),
            _make_cost_row(OUTPUT_PORT_ID_B, "Port B", "50.00", "20.00", "20.00"),
        ]
        self._setup_mocks(
            mock_stats_svc_cls,
            mock_output_port_svc_cls,
            mock_cost_svc_cls,
            mock_dp_svc_cls,
            mock_get_user,
            mock_get_token,
            mock_get_db,
            cost_rows=cost_rows,
            output_ports=[],
        )

        result = get_data_product_usage(DATA_PRODUCT_ID)

        assert result["cost_summary"]["total_cost"] == 240.0
        assert len(result["cost_summary"]["by_output_port"]) == 2

    def test_consumer_query_stats_aggregated_per_output_port(
        self,
        mock_stats_svc_cls,
        mock_output_port_svc_cls,
        mock_cost_svc_cls,
        mock_dp_svc_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
    ):
        """Query counts are summed per consumer across all days for each output port."""
        port_a = _make_output_port(OUTPUT_PORT_ID_A, "Port A")
        stats_a = _make_query_stats_response(
            [
                _make_stat("2026-04-01", CONSUMER_ID_1, "Consumer One", 100),
                _make_stat("2026-04-02", CONSUMER_ID_1, "Consumer One", 200),
                _make_stat("2026-04-01", CONSUMER_ID_2, "Consumer Two", 50),
            ]
        )
        self._setup_mocks(
            mock_stats_svc_cls,
            mock_output_port_svc_cls,
            mock_cost_svc_cls,
            mock_dp_svc_cls,
            mock_get_user,
            mock_get_token,
            mock_get_db,
            output_ports=[port_a],
            query_stats_by_port={OUTPUT_PORT_ID_A: stats_a},
        )

        result = get_data_product_usage(DATA_PRODUCT_ID)

        qs = result["consumer_query_stats"]
        assert len(qs) == 1
        port_stats = qs[0]
        assert port_stats["output_port_id"] == str(OUTPUT_PORT_ID_A)
        assert port_stats["output_port_name"] == "Port A"
        consumers = port_stats["top_consumers"]
        # Consumer One has 300 total, Consumer Two has 50 — sorted descending
        assert len(consumers) == 2
        assert consumers[0]["consumer_data_product_name"] == "Consumer One"
        assert consumers[0]["total_queries"] == 300
        assert consumers[1]["consumer_data_product_name"] == "Consumer Two"
        assert consumers[1]["total_queries"] == 50

    def test_data_product_not_found_returns_error(
        self,
        mock_stats_svc_cls,
        mock_output_port_svc_cls,
        mock_cost_svc_cls,
        mock_dp_svc_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
    ):
        """Returns error dict when data product does not exist."""
        self._setup_mocks(
            mock_stats_svc_cls,
            mock_output_port_svc_cls,
            mock_cost_svc_cls,
            mock_dp_svc_cls,
            mock_get_user,
            mock_get_token,
            mock_get_db,
            data_product=None,
        )
        mock_dp_svc_cls.return_value.get_data_product.return_value = None

        result = get_data_product_usage(DATA_PRODUCT_ID)

        assert "error" in result
        assert DATA_PRODUCT_ID in result["error"]

    def test_day_range_forwarded_to_services(
        self,
        mock_stats_svc_cls,
        mock_output_port_svc_cls,
        mock_cost_svc_cls,
        mock_dp_svc_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
    ):
        """day_range parameter is passed through to both cost and query stats services."""
        self._setup_mocks(
            mock_stats_svc_cls,
            mock_output_port_svc_cls,
            mock_cost_svc_cls,
            mock_dp_svc_cls,
            mock_get_user,
            mock_get_token,
            mock_get_db,
        )

        result = get_data_product_usage(DATA_PRODUCT_ID, day_range=90)

        assert result["day_range"] == 90
        mock_cost_svc_cls.return_value.get_data_product_cost_summary.assert_called_once()
        call_args = (
            mock_cost_svc_cls.return_value.get_data_product_cost_summary.call_args
        )
        assert call_args[0][1] == 90 or call_args[1].get("day_range") == 90

    def test_no_data_returns_empty_collections(
        self,
        mock_stats_svc_cls,
        mock_output_port_svc_cls,
        mock_cost_svc_cls,
        mock_dp_svc_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
    ):
        """When there are no cost records or output ports, returns zeros and empty lists."""
        self._setup_mocks(
            mock_stats_svc_cls,
            mock_output_port_svc_cls,
            mock_cost_svc_cls,
            mock_dp_svc_cls,
            mock_get_user,
            mock_get_token,
            mock_get_db,
            cost_rows=[],
            output_ports=[],
        )

        result = get_data_product_usage(DATA_PRODUCT_ID)

        assert "error" not in result
        assert result["cost_summary"]["total_cost"] == 0.0
        assert result["cost_summary"]["by_output_port"] == []
        assert result["consumer_query_stats"] == []
