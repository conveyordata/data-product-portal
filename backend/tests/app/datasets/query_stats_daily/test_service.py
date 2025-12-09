from datetime import date, timedelta

import pytest
from sqlalchemy.orm import Session

from app.datasets.query_stats_daily.model import DatasetQueryStatsDaily
from app.datasets.query_stats_daily.schema_request import (
    DatasetQueryStatsDailyDelete,
    DatasetQueryStatsDailyUpdate,
)
from app.datasets.query_stats_daily.service import (
    DatasetQueryStatsDailyService,
    QueryStatsGranularity,
)
from tests.factories import (
    DataProductFactory,
    DatasetFactory,
    DatasetQueryStatsDailyFactory,
)


@pytest.fixture
def dataset_with_two_stats(session: Session):
    """Return dataset + consumers with two stats already persisted."""
    dataset = DatasetFactory()
    consumer1 = DataProductFactory()
    consumer2 = DataProductFactory()
    today = date.today()

    session.add_all(
        [
            DatasetQueryStatsDailyFactory(
                date=today,
                dataset_id=dataset.id,
                consumer_data_product_id=consumer1.id,
                query_count=50,
            ),
            DatasetQueryStatsDailyFactory(
                date=today,
                dataset_id=dataset.id,
                consumer_data_product_id=consumer2.id,
                query_count=75,
            ),
        ]
    )
    session.commit()

    return dataset, today, consumer1, consumer2


@pytest.fixture
def dataset_with_daily_history(session: Session):
    """Return dataset data for get_query_stats_daily tests."""
    dataset = DatasetFactory()
    consumer1 = DataProductFactory()
    consumer2 = DataProductFactory()
    today = date.today()
    yesterday = today - timedelta(days=1)

    session.add_all(
        [
            DatasetQueryStatsDailyFactory(
                date=today,
                dataset_id=dataset.id,
                consumer_data_product_id=consumer1.id,
                query_count=100,
            ),
            DatasetQueryStatsDailyFactory(
                date=yesterday,
                dataset_id=dataset.id,
                consumer_data_product_id=consumer2.id,
                query_count=200,
            ),
        ]
    )

    other_dataset = DatasetFactory()
    session.add(
        DatasetQueryStatsDailyFactory(
            date=today,
            dataset_id=other_dataset.id,
            consumer_data_product_id=consumer1.id,
            query_count=999,
        )
    )
    session.commit()

    return dataset, today, yesterday, consumer1, consumer2


class TestDatasetQueryStatsDailyService:
    @staticmethod
    def _fetch_stats(session, dataset_id, consumer_id, target_date, *, multiple=False):
        """Return DatasetQueryStatsDaily rows for a dataset/consumer/date combo."""
        query = session.query(DatasetQueryStatsDaily).filter_by(
            date=target_date,
            dataset_id=dataset_id,
            consumer_data_product_id=consumer_id,
        )
        return query.all() if multiple else query.first()

    def test_update_query_stats_daily_single_record(self, session: Session):
        """Test updating query stats with a single record."""
        dataset = DatasetFactory()
        consumer = DataProductFactory()
        today = date.today()

        updates = [
            DatasetQueryStatsDailyUpdate(
                date=today.isoformat(),
                consumer_data_product_id=consumer.id,
                query_count=100,
            )
        ]

        service = DatasetQueryStatsDailyService(session)
        service.update_query_stats_daily(dataset.id, updates)

        stats = self._fetch_stats(session, dataset.id, consumer.id, today)

        assert stats is not None
        assert stats.query_count == 100
        assert stats.dataset_id == dataset.id
        assert stats.consumer_data_product_id == consumer.id

    def test_update_query_stats_daily_with_overlapping_updates(
        self, session: Session, dataset_with_two_stats
    ):
        """Test patching query stats where one row already exists in the table."""
        dataset, today, consumer1, consumer2 = dataset_with_two_stats
        consumer3 = DataProductFactory()

        # Patch with 2 updates: one overlapping (consumer1) and one new (consumer3)
        updates = [
            DatasetQueryStatsDailyUpdate(
                date=today.isoformat(),
                consumer_data_product_id=consumer1.id,
                query_count=100,
            ),
            DatasetQueryStatsDailyUpdate(
                date=today.isoformat(),
                consumer_data_product_id=consumer3.id,
                query_count=200,
            ),
        ]

        service = DatasetQueryStatsDailyService(session)
        service.update_query_stats_daily(dataset.id, updates)

        # Verify consumer1 was updated (not duplicated)
        stats_consumer1 = self._fetch_stats(
            session, dataset.id, consumer1.id, today, multiple=True
        )
        assert len(stats_consumer1) == 1
        assert stats_consumer1[0].query_count == 100

        # Verify consumer2 remains unchanged
        stats_consumer2 = self._fetch_stats(session, dataset.id, consumer2.id, today)
        assert stats_consumer2 is not None
        assert stats_consumer2.query_count == 75

        # Verify consumer3 was created
        stats_consumer3 = self._fetch_stats(session, dataset.id, consumer3.id, today)
        assert stats_consumer3 is not None
        assert stats_consumer3.query_count == 200

    def test_get_query_stats_daily(self, session: Session, dataset_with_daily_history):
        """Test getting query stats for a dataset."""
        dataset, today, yesterday, consumer1, consumer2 = dataset_with_daily_history

        # Get stats for the dataset
        service = DatasetQueryStatsDailyService(session)
        response = service.get_query_stats_daily(
            dataset.id,
            granularity=QueryStatsGranularity.DAY,
            day_range=365,
        )
        stats = response.dataset_query_stats_daily_responses

        # Verify buckets are filled (should have many entries due to bucket filling)
        assert len(stats) > 2

        # Filter to actual data points (non-zero query counts)
        actual_stats = [stat for stat in stats if stat.query_count > 0]
        assert len(actual_stats) == 2

        # Verify the correct records were returned
        stats_by_consumer = {
            stat.consumer_data_product_id: stat for stat in actual_stats
        }
        assert consumer1.id in stats_by_consumer
        assert consumer2.id in stats_by_consumer
        assert stats_by_consumer[consumer1.id].query_count == 100
        assert stats_by_consumer[consumer2.id].query_count == 200

        # Verify dates line up with expected history
        assert stats_by_consumer[consumer1.id].date == today
        assert stats_by_consumer[consumer2.id].date == yesterday

    def test_get_query_stats_daily_week_granularity(self, session: Session):
        dataset = DatasetFactory()
        consumer = DataProductFactory()

        base_date = date.today() - timedelta(days=7)
        start_of_week = base_date - timedelta(days=base_date.weekday())
        middle_of_week = start_of_week + timedelta(days=2)

        DatasetQueryStatsDailyFactory(
            date=start_of_week,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer.id,
            query_count=120,
        )
        DatasetQueryStatsDailyFactory(
            date=middle_of_week,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer.id,
            query_count=180,
        )
        session.commit()

        service = DatasetQueryStatsDailyService(session)
        day_range = 14
        response = service.get_query_stats_daily(
            dataset.id,
            granularity=QueryStatsGranularity.WEEK,
            day_range=day_range,
        )

        stats = response.dataset_query_stats_daily_responses

        # Calculate expected number of week buckets: from (today - day_range) to today, aligned to weeks
        # This matches the logic in _fill_missing_buckets -> _build_buckets
        range_start = date.today() - timedelta(days=day_range)
        start_week = QueryStatsGranularity.WEEK.align_date(range_start)
        end_week = QueryStatsGranularity.WEEK.align_date(date.today())

        # Count weeks from start_week to end_week (inclusive)
        week_count = 0
        current = start_week
        while current <= end_week:
            week_count += 1
            current = QueryStatsGranularity.WEEK.increment_date(current)

        # With 1 consumer, we expect week_count entries (one per week bucket)
        expected_count = week_count
        assert len(stats) == expected_count

        # Find the actual data point (non-zero query count)
        actual_stats = [stat for stat in stats if stat.query_count > 0]
        assert len(actual_stats) == 1
        assert actual_stats[0].date == start_of_week
        assert actual_stats[0].query_count == 300
        assert actual_stats[0].consumer_data_product_id == consumer.id

    def test_get_query_stats_daily_day_range_filter(self, session: Session):
        dataset = DatasetFactory()
        consumer = DataProductFactory()

        recent_date = date.today() - timedelta(days=10)
        old_date = date.today() - timedelta(days=120)

        DatasetQueryStatsDailyFactory(
            date=recent_date,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer.id,
            query_count=50,
        )
        DatasetQueryStatsDailyFactory(
            date=old_date,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer.id,
            query_count=75,
        )
        session.commit()

        service = DatasetQueryStatsDailyService(session)
        response = service.get_query_stats_daily(
            dataset.id,
            granularity=QueryStatsGranularity.DAY,
            day_range=30,
        )

        stats = response.dataset_query_stats_daily_responses
        # Today + 30 days ago = 31 days
        assert len(stats) == 31

        # Find the actual data point (non-zero query count)
        actual_stats = [stat for stat in stats if stat.query_count > 0]
        assert len(actual_stats) == 1
        assert actual_stats[0].date == recent_date
        assert actual_stats[0].query_count == 50

    def test_delete_query_stats_daily_existing_row(
        self, session: Session, dataset_with_two_stats
    ):
        dataset, today, consumer1, consumer2 = dataset_with_two_stats
        service = DatasetQueryStatsDailyService(session)

        service.delete_query_stats_daily(
            dataset.id,
            DatasetQueryStatsDailyDelete(
                date=today.isoformat(),
                consumer_data_product_id=consumer1.id,
            ),
        )

        deleted_row = self._fetch_stats(session, dataset.id, consumer1.id, today)
        remaining_row = self._fetch_stats(session, dataset.id, consumer2.id, today)

        assert deleted_row is None
        assert remaining_row.consumer_data_product_id == consumer2.id
