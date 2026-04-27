from datetime import UTC, datetime, time, timedelta

from app.data_products.output_ports.freshness.enums import FreshnessStatus
from app.data_products.output_ports.freshness.model import (
    FreshnessObservation,
    FreshnessSlo,
)
from tests.factories import DatasetFactory

ENDPOINT = "/api/v2/data_products"


class TestFreshnessStatusComputation:
    def test_freshness_status_is_none_when_no_slo(self, session):
        dataset = DatasetFactory()
        session.refresh(dataset)
        assert dataset.freshness_status is None
        assert dataset.freshness_deadline_time is None

    def test_freshness_status_is_unknown_when_slo_but_no_observations(self, session):
        dataset = DatasetFactory()
        slo = FreshnessSlo(
            output_port_id=dataset.id,
            deadline_time=time(8, 0, 0),
        )
        session.add(slo)
        session.commit()
        session.refresh(dataset)
        assert dataset.freshness_status == FreshnessStatus.UNKNOWN.value

    def test_freshness_status_is_fresh_when_refreshed_today(self, session):
        dataset = DatasetFactory()
        slo = FreshnessSlo(
            output_port_id=dataset.id,
            deadline_time=time(8, 0, 0),
        )
        session.add(slo)
        obs = FreshnessObservation(
            output_port_id=dataset.id,
            last_refreshed_at=datetime.now(UTC).replace(hour=7, minute=0),
        )
        session.add(obs)
        session.commit()
        session.refresh(dataset)
        assert dataset.freshness_status == FreshnessStatus.FRESH.value

    def test_freshness_status_is_stale_when_not_refreshed_today_past_deadline(
        self, session
    ):
        dataset = DatasetFactory()
        slo = FreshnessSlo(
            output_port_id=dataset.id,
            deadline_time=time(0, 0, 1),  # 00:00:01 UTC — always past
        )
        session.add(slo)
        obs = FreshnessObservation(
            output_port_id=dataset.id,
            last_refreshed_at=datetime.now(UTC) - timedelta(days=2),
        )
        session.add(obs)
        session.commit()
        session.refresh(dataset)
        assert dataset.freshness_status == FreshnessStatus.STALE.value
