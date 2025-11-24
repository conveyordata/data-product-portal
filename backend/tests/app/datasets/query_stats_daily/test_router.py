from datetime import date, timedelta

from tests.factories import (
    DataProductFactory,
    DatasetFactory,
    DatasetQueryStatsDailyFactory,
)

from app.datasets.query_stats_daily.model import DatasetQueryStatsDaily

ENDPOINT = "/api/datasets"


class TestDatasetQueryStatsDailyRouter:
    def test_update_query_stats_daily_batch(self, client, session):
        """Test batch updating query stats."""
        dataset = DatasetFactory()
        consumer1 = DataProductFactory()
        consumer2 = DataProductFactory()
        today = date.today()

        update_payload = {
            "dataset_query_stats_daily_updates": [
                {
                    "date": today.isoformat(),
                    "consumer_data_product_id": str(consumer1.id),
                    "query_count": 150,
                },
                {
                    "date": (today - timedelta(days=1)).isoformat(),
                    "consumer_data_product_id": str(consumer2.id),
                    "query_count": 250,
                },
            ]
        }

        response = client.patch(
            f"{ENDPOINT}/{dataset.id}/query_stats", json=update_payload
        )

        assert response.status_code == 200

        # Verify the records were created
        stats = session.query(DatasetQueryStatsDaily).all()
        assert len(stats) >= 2

    def test_get_query_stats(self, client, session):
        """Test getting query stats for a dataset."""
        dataset = DatasetFactory()
        consumer1 = DataProductFactory()
        consumer2 = DataProductFactory()
        today = date.today()
        yesterday = today - timedelta(days=1)

        DatasetQueryStatsDailyFactory(
            date=today,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer1.id,
            query_count=150,
        )
        DatasetQueryStatsDailyFactory(
            date=yesterday,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer2.id,
            query_count=250,
        )
        session.commit()

        response = client.get(f"{ENDPOINT}/{dataset.id}/query_stats")

        assert response.status_code == 200

        data = response.json()
        assert "dataset_query_stats_daily_responses" in data
        stats = data["dataset_query_stats_daily_responses"]
        assert len(stats) == 2

        for stat in stats:
            assert "date" in stat
            assert "consumer_data_product_id" in stat
            assert "query_count" in stat
            assert stat["query_count"] in [150, 250]

    def test_delete_query_stat(self, client, session):
        dataset = DatasetFactory()
        consumer = DataProductFactory()
        today = date.today()

        DatasetQueryStatsDailyFactory(
            date=today,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer.id,
            query_count=200,
        )
        session.commit()

        payload = {
            "date": today.isoformat(),
            "consumer_data_product_id": str(consumer.id),
        }

        response = client.request(
            "DELETE", f"{ENDPOINT}/{dataset.id}/query_stats", json=payload
        )

        assert response.status_code == 200
        stats = session.query(DatasetQueryStatsDaily).all()
        assert stats == []

    def test_get_query_stats_with_query_params(self, client, session):
        dataset = DatasetFactory()
        consumer = DataProductFactory()
        base_date = date.today() - timedelta(days=7)
        start_of_week = base_date - timedelta(days=base_date.weekday())
        middle_of_week = start_of_week + timedelta(days=2)
        old_date = date.today() - timedelta(days=150)

        DatasetQueryStatsDailyFactory(
            date=start_of_week,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer.id,
            query_count=50,
        )
        DatasetQueryStatsDailyFactory(
            date=middle_of_week,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer.id,
            query_count=75,
        )
        DatasetQueryStatsDailyFactory(
            date=old_date,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer.id,
            query_count=125,
        )
        session.commit()

        response = client.get(
            f"{ENDPOINT}/{dataset.id}/query_stats",
            params={"granularity": "week", "time_range": "90d"},
        )

        assert response.status_code == 200
        data = response.json()
        stats = data["dataset_query_stats_daily_responses"]
        assert len(stats) == 1
        assert stats[0]["date"] == start_of_week.isoformat()
        assert stats[0]["query_count"] == 125
