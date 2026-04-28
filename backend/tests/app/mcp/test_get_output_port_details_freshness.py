# ruff: noqa: S106
from datetime import UTC, datetime, time
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.data_products.output_ports.freshness.enums import FreshnessStatus
from app.mcp.mcp import get_output_port_details

OUTPUT_PORT_ID = str(uuid4())

_BASE_RESULT = {
    "id": OUTPUT_PORT_ID,
    "name": "my-output-port",
    "description": "desc",
}


def _mock_dataset(
    freshness_status=None,
    freshness_deadline_time=None,
    latest_freshness_at=None,
):
    ds = MagicMock()
    ds.id = OUTPUT_PORT_ID
    ds.freshness_status = freshness_status
    ds.freshness_deadline_time = freshness_deadline_time
    ds.latest_freshness_at = latest_freshness_at
    return ds


def _mock_validated_response():
    mock = MagicMock()
    mock.model_dump.return_value = dict(_BASE_RESULT)
    return mock


@patch("app.mcp.mcp.get_db_session")
@patch("app.mcp.mcp.get_access_token")
@patch("app.mcp.mcp.get_mcp_authenticated_user")
@patch("app.mcp.mcp.OutputPortService")
@patch("app.mcp.mcp.GetOutputPortResponse")
class TestGetOutputPortDetailsFreshness:
    def test_freshness_with_slo_and_observation(
        self,
        mock_response_cls,
        mock_output_port_service_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
    ):
        """SLO configured + observation exists → freshness block with computed status."""
        mock_get_db.return_value = iter([MagicMock()])
        mock_get_token.return_value = MagicMock(token="tok")
        mock_get_user.return_value = {"id": str(uuid4())}
        mock_output_port_service_cls.return_value.get_dataset.return_value = (
            _mock_dataset(
                freshness_status=FreshnessStatus.FRESH.value,
                freshness_deadline_time=time(8, 0, 0),
                latest_freshness_at=datetime(2026, 4, 28, 7, 0, 0, tzinfo=UTC),
            )
        )
        mock_response_cls.model_validate.return_value = _mock_validated_response()

        result = get_output_port_details(OUTPUT_PORT_ID)

        assert "freshness" in result
        f = result["freshness"]
        assert f["status"] == "fresh"
        assert f["slo_deadline"] == "08:00:00"
        assert f["last_refreshed_at"] == "2026-04-28T07:00:00+00:00"

    def test_freshness_with_slo_no_observation(
        self,
        mock_response_cls,
        mock_output_port_service_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
    ):
        """SLO configured but no observations → status unknown, timestamps null."""
        mock_get_db.return_value = iter([MagicMock()])
        mock_get_token.return_value = MagicMock(token="tok")
        mock_get_user.return_value = {"id": str(uuid4())}
        mock_output_port_service_cls.return_value.get_dataset.return_value = (
            _mock_dataset(
                freshness_status=FreshnessStatus.UNKNOWN.value,
                freshness_deadline_time=time(8, 0, 0),
                latest_freshness_at=None,
            )
        )
        mock_response_cls.model_validate.return_value = _mock_validated_response()

        result = get_output_port_details(OUTPUT_PORT_ID)

        assert "freshness" in result
        f = result["freshness"]
        assert f["status"] == "unknown"
        assert f["slo_deadline"] == "08:00:00"
        assert f["last_refreshed_at"] is None

    def test_freshness_no_slo(
        self,
        mock_response_cls,
        mock_output_port_service_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
    ):
        """No SLO configured → status unknown, all freshness fields null."""
        mock_get_db.return_value = iter([MagicMock()])
        mock_get_token.return_value = MagicMock(token="tok")
        mock_get_user.return_value = {"id": str(uuid4())}
        mock_output_port_service_cls.return_value.get_dataset.return_value = (
            _mock_dataset(
                freshness_status=None,
                freshness_deadline_time=None,
                latest_freshness_at=None,
            )
        )
        mock_response_cls.model_validate.return_value = _mock_validated_response()

        result = get_output_port_details(OUTPUT_PORT_ID)

        assert "freshness" in result
        f = result["freshness"]
        assert f["status"] == "unknown"
        assert f["slo_deadline"] is None
        assert f["last_refreshed_at"] is None
