from datetime import date, timedelta
from decimal import Decimal

from tests.factories import (
    DataProductFactory,
    DatasetFactory,
    OutputPortCostRecordFactory,
)

ENDPOINT = "/api/v2/data_products"


class TestDataProductCostSummary:
    def test_get_cost_summary_single_output_port(self, client, session):
        data_product = DataProductFactory()
        dataset = DatasetFactory(data_product=data_product)
        OutputPortCostRecordFactory(
            output_port_id=dataset.id,
            recorded_at=date.today() - timedelta(days=5),
            compute_cost=Decimal("80.00"),
            storage_cost=Decimal("40.00"),
            platform_overhead_cost=Decimal("30.00"),
        )

        response = client.get(f"{ENDPOINT}/{data_product.id}/cost")
        assert response.status_code == 200
        body = response.json()
        assert body["data_product_id"] == str(data_product.id)
        assert body["day_range"] == 30
        assert len(body["breakdown"]) == 1
        item = body["breakdown"][0]
        assert item["output_port_id"] == str(dataset.id)
        assert item["output_port_name"] == dataset.name
        assert Decimal(item["compute_cost"]) == Decimal("80.00")
        assert Decimal(item["total_cost"]) == Decimal("150.00")
        assert Decimal(body["total_cost"]) == Decimal("150.00")

    def test_get_cost_summary_multiple_output_ports(self, client, session):
        data_product = DataProductFactory()
        dataset_a = DatasetFactory(data_product=data_product)
        dataset_b = DatasetFactory(data_product=data_product)
        OutputPortCostRecordFactory(
            output_port_id=dataset_a.id,
            recorded_at=date.today() - timedelta(days=5),
            compute_cost=Decimal("80.00"),
            storage_cost=Decimal("40.00"),
            platform_overhead_cost=Decimal("30.00"),
        )
        OutputPortCostRecordFactory(
            output_port_id=dataset_b.id,
            recorded_at=date.today() - timedelta(days=5),
            compute_cost=Decimal("50.00"),
            storage_cost=Decimal("20.00"),
            platform_overhead_cost=Decimal("20.00"),
        )

        response = client.get(f"{ENDPOINT}/{data_product.id}/cost")
        assert response.status_code == 200
        body = response.json()
        assert len(body["breakdown"]) == 2
        assert Decimal(body["total_cost"]) == Decimal("240.00")

    def test_get_cost_summary_sums_records_in_window(self, client, session):
        """Two records for the same output port within the window are summed."""
        data_product = DataProductFactory()
        dataset = DatasetFactory(data_product=data_product)
        OutputPortCostRecordFactory(
            output_port_id=dataset.id,
            recorded_at=date.today() - timedelta(days=5),
            compute_cost=Decimal("40.00"),
            storage_cost=Decimal("20.00"),
            platform_overhead_cost=Decimal("10.00"),
        )
        OutputPortCostRecordFactory(
            output_port_id=dataset.id,
            recorded_at=date.today() - timedelta(days=10),
            compute_cost=Decimal("40.00"),
            storage_cost=Decimal("20.00"),
            platform_overhead_cost=Decimal("10.00"),
        )

        response = client.get(f"{ENDPOINT}/{data_product.id}/cost?day_range=30")
        assert response.status_code == 200
        body = response.json()
        assert Decimal(body["total_cost"]) == Decimal("140.00")

    def test_get_cost_summary_excludes_records_outside_window(self, client, session):
        data_product = DataProductFactory()
        dataset = DatasetFactory(data_product=data_product)
        # Inside window
        OutputPortCostRecordFactory(
            output_port_id=dataset.id,
            recorded_at=date.today() - timedelta(days=5),
            compute_cost=Decimal("80.00"),
            storage_cost=Decimal("40.00"),
            platform_overhead_cost=Decimal("30.00"),
        )
        # Outside window
        OutputPortCostRecordFactory(
            output_port_id=dataset.id,
            recorded_at=date.today() - timedelta(days=100),
            compute_cost=Decimal("999.00"),
            storage_cost=Decimal("999.00"),
            platform_overhead_cost=Decimal("999.00"),
        )

        response = client.get(f"{ENDPOINT}/{data_product.id}/cost?day_range=30")
        assert response.status_code == 200
        body = response.json()
        assert Decimal(body["total_cost"]) == Decimal("150.00")

    def test_get_cost_summary_no_data_returns_empty(self, client, session):
        data_product = DataProductFactory()
        DatasetFactory(data_product=data_product)

        response = client.get(f"{ENDPOINT}/{data_product.id}/cost")
        assert response.status_code == 200
        body = response.json()
        assert body["breakdown"] == []
        assert Decimal(body["total_cost"]) == Decimal(0)

    def test_get_cost_summary_respects_day_range_param(self, client, session):
        data_product = DataProductFactory()
        dataset = DatasetFactory(data_product=data_product)
        OutputPortCostRecordFactory(
            output_port_id=dataset.id,
            recorded_at=date.today() - timedelta(days=5),
            compute_cost=Decimal("50.00"),
            storage_cost=Decimal("0.00"),
            platform_overhead_cost=Decimal("0.00"),
        )

        response = client.get(f"{ENDPOINT}/{data_product.id}/cost?day_range=90")
        assert response.status_code == 200
        body = response.json()
        assert body["day_range"] == 90
        assert Decimal(body["total_cost"]) == Decimal("50.00")
