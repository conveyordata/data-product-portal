from datetime import date, timedelta

from app.authorization.roles.schema import Scope
from app.core.authz.actions import AuthorizationAction
from app.data_products.output_ports.query_stats.model import (
    DatasetQueryStatsDaily,
)
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetFactory,
    DatasetQueryStatsFactory,
    RoleFactory,
    UserFactory,
)

ENDPOINT = "/api/datasets"
DATA_PRODUCT_ENDPOINT = "/api/v2/data_products"


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

        DatasetQueryStatsFactory(
            date=today,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer1.id,
            query_count=150,
        )
        DatasetQueryStatsFactory(
            date=yesterday,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer2.id,
            query_count=250,
        )
        session.commit()

        # Use day granularity with small day_range to avoid excessive bucket filling
        response = client.get(
            f"{ENDPOINT}/{dataset.id}/query_stats",
            params={"granularity": "day", "day_range": 7},
        )

        assert response.status_code == 200

        data = response.json()
        assert "dataset_query_stats_daily_responses" in data
        stats = data["dataset_query_stats_daily_responses"]

        # Find the actual data points (non-zero query counts)
        actual_stats = [stat for stat in stats if stat["query_count"] > 0]
        assert len(actual_stats) == 2

        for stat in actual_stats:
            assert "date" in stat
            assert "consumer_data_product_id" in stat
            assert "query_count" in stat
            assert stat["query_count"] in [150, 250]

    def test_delete_query_stat(self, client, session):
        dataset = DatasetFactory()
        consumer = DataProductFactory()
        today = date.today()

        DatasetQueryStatsFactory(
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

        DatasetQueryStatsFactory(
            date=start_of_week,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer.id,
            query_count=50,
        )
        DatasetQueryStatsFactory(
            date=middle_of_week,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer.id,
            query_count=75,
        )
        DatasetQueryStatsFactory(
            date=old_date,
            dataset_id=dataset.id,
            consumer_data_product_id=consumer.id,
            query_count=125,
        )
        session.commit()

        response = client.get(
            f"{ENDPOINT}/{dataset.id}/query_stats",
            params={"granularity": "week", "day_range": 90},
        )

        assert response.status_code == 200
        data = response.json()
        stats = data["dataset_query_stats_daily_responses"]

        # The service fills missing buckets, so we'll get all weeks in the 90-day range
        # Find the week with actual data (start_of_week and middle_of_week are in same week)
        # They should be aggregated together: 50 + 75 = 125
        actual_stats = [stat for stat in stats if stat["query_count"] > 0]
        assert len(actual_stats) == 1
        assert actual_stats[0]["date"] == start_of_week.isoformat()
        assert actual_stats[0]["query_count"] == 125

        # Verify that all stats have the expected structure
        for stat in stats:
            assert "date" in stat
            assert "consumer_data_product_id" in stat
            assert "query_count" in stat
            assert "consumer_data_product_name" in stat

    def test_delete_data_product_cascades_query_stats_daily(self, client, session):
        """Regression test: Verify that deleting a data product via API cascade deletes query stats."""

        data_product = DataProductFactory()
        dataset = DatasetFactory(data_product=data_product, tags=[])
        consumer = DataProductFactory()

        DatasetQueryStatsFactory(
            date=date(2024, 1, 15),
            dataset_id=dataset.id,
            consumer_data_product_id=consumer.id,
            query_count=150,
        )
        session.commit()

        # Store dataset_id before deletion (dataset object will be deleted)
        dataset_id = dataset.id

        # Verify query stats exist before deletion
        stats_before = (
            session.query(DatasetQueryStatsDaily).filter_by(dataset_id=dataset_id).all()
        )
        assert len(stats_before) == 1, "Should have 1 query stat before deletion"

        # Set up authorization to allow data product deletion
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[AuthorizationAction.DATA_PRODUCT__DELETE],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        session.commit()

        # Delete the data product via API
        response = client.delete(f"{DATA_PRODUCT_ENDPOINT}/{data_product.id}")
        assert response.status_code == 200, "Data product deletion should succeed"

        # Verify that query stats are cascade deleted by the database
        # (This happens because deleting the data product cascades to delete the dataset,
        # and deleting the dataset cascades to delete the query stats)
        stats_after = (
            session.query(DatasetQueryStatsDaily).filter_by(dataset_id=dataset_id).all()
        )
        assert len(stats_after) == 0, (
            "Query stats should be cascade deleted when data product (and its dataset) is deleted"
        )
