import time
from typing import Final

from sqlalchemy import text

from app.authorization.roles.service import RoleService
from app.data_products.output_ports.schema_response import (
    GetDataProductOutputPortsResponse,
)
from app.data_products.output_ports.service import OutputPortService
from tests.factories import DatasetFactory

EMBEDDING_LATENCY_BOUND: Final[float] = 2.000  # seconds
LATENCY_BOUND: Final[float] = 0.300  # seconds
PRECISION_BOUND: Final[float] = 0.10
RECALL_BOUND: Final[float] = 0.7


class TestOutputPortSearchRouter:
    def test_search_datasets(self, session, client):
        ds_1, ds_2, ds_3 = self.setup(session)

        response = client.get("/api/datasets/search", params={"query": "Data"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) >= 2
        returned_ops = {item["name"] for item in data}
        expected_ops = {ds_1.name, ds_2.name}
        assert returned_ops.issuperset(expected_ops), (
            f"{returned_ops} is not the superset of {expected_ops}"
        )

    def test_search_output_ports(self, session, client):
        ds_1, ds_2, ds_3 = self.setup(session)

        response = client.get("/api/v2/search/output_ports", params={"query": "Data"})
        assert response.status_code == 200, response.text
        output = GetDataProductOutputPortsResponse.model_validate(response.json())
        assert len(output.output_ports) >= 2
        returned_ops = {port.name for port in output.output_ports}
        expected_ops = {ds_1.name, ds_2.name}
        assert returned_ops.issuperset(expected_ops), (
            f"{returned_ops} is not the superset of {expected_ops}"
        )

    def test_benchmark_output_ports(self, session, client):
        self.reseed(session)

        configuration = [
            {
                "query": "retention",
                "expected": {
                    "Daily Feature Engagement",
                    "Monthly Churn Targets",
                    "Top Engaged Segments",
                    "Weekly Churn Probabilities",
                },
                "recall_bound": 0.50
            },
            {
                "query": "Which campaigns delivered the best ROI?",
                "expected": {
                    "Ab Test Outcomes",
                    "Ad Spend Vs Roi",
                    "Campaign Performance Summary",
                },
                "precision_bound": 0.05,
            },
            {
                "query": "Which features are used the most?",
                "expected": {
                    "Daily Feature Engagement",
                    "Product KPI Dashboard",
                    "Release Engagement By Segment",
                    "Release Impact Summary",
                    "Weekly Feature Summary",
                },
                "recall_bound": 0.6,
            },
            {
                "query": "Are we GDPR compliant?",
                "expected": {"Privacy Compliance Report", "Regulatory Audit Report"},
                "precision_bound": 0.05,
            },
            {
                "query": "What will our expenses look like next quarter?",
                "expected": {"Expense Forecast"},
                "precision_bound": 0.05
            },
            {
                "query": "Planned versus actual production",
                "expected": {
                    "Production Planning Forecast",
                    "Production Variance Report",
                },
            },
            {
                "query": "inventory levels by warehouse",
                "expected": {"Inventory Status"},
                "precision_bound": 0.05
            },
        ]

        # Validate test configuration
        valid_output_ports = {
            port.name for port in OutputPortService(session).get_output_ports(None)
        }
        for config in configuration:
            for value in config["expected"]:
                assert value in valid_output_ports, (
                    f"{value} is not registered as the name of an Output Port"
                )

        avg_precision, avg_recall = 0, 0
        for config in configuration:
            precision, recall = self._run_benchmark(client, **config)
            avg_precision += precision
            avg_recall += recall
        avg_precision /= len(configuration)
        avg_recall /= len(configuration)
        assert avg_precision >= PRECISION_BOUND, (
            f"Average precision score too low ({avg_precision} < {PRECISION_BOUND})"
        )
        assert avg_recall >= RECALL_BOUND, (
            f"Average recall score too ({avg_recall} < {PRECISION_BOUND})"
        )

    @staticmethod
    def _run_benchmark(
        client,
        *,
        query: str,
        expected: set[str],
        latency_bound: float = LATENCY_BOUND,
        precision_bound: float = PRECISION_BOUND,
        recall_bound: float = RECALL_BOUND,
    ) -> tuple[float, float]:
        start_time = time.perf_counter()
        response = client.get(
            "/api/v2/search/output_ports",
            params={"query": query, "limit": 10},
        )
        end_time = time.perf_counter()

        assert response.status_code == 200, response.text
        assert end_time - start_time < latency_bound, (
            f"Output Port search took longer than {latency_bound * 1000} ms"
        )

        output = GetDataProductOutputPortsResponse.model_validate(response.json())

        positives = {port.name for port in output.output_ports}
        true_positives = len(expected.intersection(positives))
        false_negatives = len(expected.difference(positives))

        precision = true_positives / len(positives)
        recall = true_positives / (true_positives + false_negatives)

        assert precision >= precision_bound, (
            f"Precision score too low for query '{query}' ({precision} < {precision_bound})"
        )
        assert recall >= recall_bound, (
            f"Recall score too low for query '{query}' ({recall} < {recall_bound})"
        )
        return precision, recall

    def setup(self, session):
        RoleService(db=session).initialize_prototype_roles()
        ds_1 = DatasetFactory(name="Customer Data")
        ds_2 = DatasetFactory(name="Sales Data")
        ds_3 = DatasetFactory(name="Internal Metrics")
        OutputPortService(db=session).recalculate_all_embeddings()
        return ds_1, ds_2, ds_3

    def reseed(self, session):
        from app.database.database import Base
        from app.db_tool import seed_cmd

        tables_list = ", ".join(
            [str(name) for name in reversed(Base.metadata.sorted_tables)]
        )
        session.execute(text(f"TRUNCATE TABLE {tables_list} RESTART IDENTITY CASCADE;"))
        session.commit()

        seed_cmd(path="./sample_data.sql")
        RoleService(db=session).initialize_prototype_roles()

        start_time = time.perf_counter()
        OutputPortService(db=session).recalculate_all_embeddings()
        end_time = time.perf_counter()
        assert (duration := end_time - start_time) <= EMBEDDING_LATENCY_BOUND, (
            f"Embeddings take too long to calculate ({duration} > {EMBEDDING_LATENCY_BOUND})"
        )
