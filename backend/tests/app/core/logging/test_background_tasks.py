import asyncio
from unittest.mock import MagicMock, patch

import pytest

from app.authorization.role_assignments.enums import DecisionStatus
from app.core.logging.posthog_analytics import report_consumption_metrics_task
from tests.factories import ExplorationFactory, InputPortFactory


class TestReportConsumptionMetricsTask:
    @pytest.mark.asyncio
    async def test_reports_total_approved_input_ports_split_by_type(self):
        exploration = ExplorationFactory()
        InputPortFactory(status=DecisionStatus.APPROVED)
        InputPortFactory(status=DecisionStatus.APPROVED)
        InputPortFactory(
            status=DecisionStatus.APPROVED,
            consuming_abstract_data_product=exploration,
        )
        InputPortFactory(status=DecisionStatus.PENDING)

        mock_posthog = MagicMock()

        with (
            patch(
                "app.core.logging.posthog_analytics.get_posthog_client",
                return_value=mock_posthog,
            ),
            patch(
                "app.core.logging.posthog_analytics._seconds_until_next_midnight_utc",
                return_value=0,
            ),
            patch(
                "app.core.logging.posthog_analytics.asyncio.sleep",
                side_effect=[None, asyncio.CancelledError()],
            ),
            pytest.raises(asyncio.CancelledError),
        ):
            await report_consumption_metrics_task()

        mock_posthog.capture.assert_called_once()
        call_kwargs = mock_posthog.capture.call_args.kwargs
        assert call_kwargs["event"] == "Daily Consumption Metrics"
        props = call_kwargs["properties"]
        assert props["total_approved_input_ports"] == 3
        assert props["approved_input_ports_data_products"] == 2
        assert props["approved_input_ports_explorations"] == 1

    @pytest.mark.asyncio
    async def test_skips_capture_when_posthog_disabled(self):
        InputPortFactory(status=DecisionStatus.APPROVED)

        with (
            patch(
                "app.core.logging.posthog_analytics.get_posthog_client",
                return_value=None,
            ),
            patch(
                "app.core.logging.posthog_analytics._seconds_until_next_midnight_utc",
                return_value=0,
            ),
            patch(
                "app.core.logging.posthog_analytics.asyncio.sleep",
                side_effect=[None],
            ),
        ):
            await report_consumption_metrics_task()
