from datetime import date, timedelta

from sqlalchemy.orm import Session
from tests.factories import (
    DataProductFactory,
    DatasetFactory,
    DatasetQueryStatsDailyFactory,
)

from app.datasets.query_stats_daily.model import DatasetQueryStatsDaily
from app.datasets.query_stats_daily.schema_request import DatasetQueryStatsDailyUpdate
from app.datasets.query_stats_daily.service import DatasetQueryStatsDailyService


class TestDatasetQueryStatsDailyService:
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

        stats = (
            session.query(DatasetQueryStatsDaily)
            .filter_by(
                date=today,
                dataset_id=dataset.id,
                consumer_data_product_id=consumer.id,
            )
            .first()
        )

        assert stats is not None
        assert stats.query_count == 100
        assert stats.dataset_id == dataset.id
        assert stats.consumer_data_product_id == consumer.id

    def test_update_query_stats_daily_with_overlapping_updates(self, session: Session):
        """Test patching query stats where one row already exists in the table."""
        dataset = DatasetFactory()
        consumer1 = DataProductFactory()
        consumer2 = DataProductFactory()
        consumer3 = DataProductFactory()
        today = date.today()

        # Create 2 existing records
        existing_stats_1 = DatasetQueryStatsDailyFactory(
            date=today,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer1.id,
            query_count=50,
        )
        existing_stats_2 = DatasetQueryStatsDailyFactory(
            date=today,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer2.id,
            query_count=75,
        )
        session.add_all([existing_stats_1, existing_stats_2])
        session.commit()

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
        stats_consumer1 = (
            session.query(DatasetQueryStatsDaily)
            .filter_by(
                date=today,
                dataset_id=dataset.id,
                consumer_data_product_id=consumer1.id,
            )
            .all()
        )
        assert len(stats_consumer1) == 1
        assert stats_consumer1[0].query_count == 100

        # Verify consumer2 remains unchanged
        stats_consumer2 = (
            session.query(DatasetQueryStatsDaily)
            .filter_by(
                date=today,
                dataset_id=dataset.id,
                consumer_data_product_id=consumer2.id,
            )
            .first()
        )
        assert stats_consumer2 is not None
        assert stats_consumer2.query_count == 75

        # Verify consumer3 was created
        stats_consumer3 = (
            session.query(DatasetQueryStatsDaily)
            .filter_by(
                date=today,
                dataset_id=dataset.id,
                consumer_data_product_id=consumer3.id,
            )
            .first()
        )
        assert stats_consumer3 is not None
        assert stats_consumer3.query_count == 200

        # Verify total count is 3
        total_stats = (
            session.query(DatasetQueryStatsDaily)
            .filter_by(
                date=today,
                dataset_id=dataset.id,
            )
            .count()
        )
        assert total_stats == 3

    def test_get_query_stats_daily(self, session: Session):
        """Test getting query stats for a dataset."""
        dataset = DatasetFactory()
        consumer1 = DataProductFactory()
        consumer2 = DataProductFactory()
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Create test data
        DatasetQueryStatsDailyFactory(
            date=today,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer1.id,
            query_count=100,
        )
        DatasetQueryStatsDailyFactory(
            date=yesterday,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer2.id,
            query_count=200,
        )

        # Create data for a different dataset (should not be returned)
        other_dataset = DatasetFactory()
        DatasetQueryStatsDailyFactory(
            date=today,
            dataset_id=other_dataset.id,
            consumer_data_product_id=consumer1.id,
            query_count=999,
        )
        session.commit()

        # Get stats for the dataset
        service = DatasetQueryStatsDailyService(session)
        stats = service.get_query_stats_daily(dataset.id)

        # Verify results
        assert len(stats) == 2
        assert all(stat.dataset_id == dataset.id for stat in stats)

        # Verify the correct records were returned
        stats_by_consumer = {stat.consumer_data_product_id: stat for stat in stats}
        assert consumer1.id in stats_by_consumer
        assert consumer2.id in stats_by_consumer
        assert stats_by_consumer[consumer1.id].query_count == 100
        assert stats_by_consumer[consumer2.id].query_count == 200
