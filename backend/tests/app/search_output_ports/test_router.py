import os
import time
from typing import Final

from sqlalchemy import text

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Prototype, Scope
from app.authorization.roles.service import RoleService
from app.data_products.output_ports.model import Dataset
from app.data_products.output_ports.schema_response import (
    GetDataProductOutputPortsResponse,
)
from app.data_products.output_ports.service import OutputPortService
from app.settings import settings
from tests.factories import (
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

EMBEDDING_LATENCY_BOUND: Final[float] = float(
    os.getenv("TEST_EMBEDDING_LATENCY_BOUND", 1.000)
)  # seconds
LATENCY_BOUND: Final[float] = 0.300  # seconds
PRECISION_BOUND: Final[float] = 0.5
RECALL_BOUND: Final[float] = 0.8


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

    def test_search_output_ports_current_user_assigned(self, session, client):
        ds_1, _, _ = self.setup(session)

        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(scope=Scope.DATASET, prototype=Prototype.OWNER)
        DatasetRoleAssignmentFactory(
            dataset=ds_1,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        response = client.get(
            "/api/v2/search/output_ports", params={"current_user_assigned": True}
        )
        assert response.status_code == 200, response.text
        output = GetDataProductOutputPortsResponse.model_validate(response.json())
        assert len(output.output_ports) == 1

    def test_search_output_ports_no_query(self, session, client):
        output_ports = self.setup(session)

        response = client.get("/api/v2/search/output_ports")
        assert response.status_code == 200, response.text
        output = GetDataProductOutputPortsResponse.model_validate(response.json())
        assert len(output.output_ports) == len(output_ports)

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
                "recall_bound": 0.25,
                "precision_bound": 0.15,
            },
            {
                "query": "Which campaigns delivered the best ROI?",
                "expected": {
                    "Ab Test Outcomes",
                    "Ad Spend Vs Roi",
                    "Campaign Performance Summary",
                },
                "limit": 5,
                "recall_bound": 0.65,
                "precision_bound": 0.4,
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
            },
            {
                "query": "Are we GDPR compliant?",
                "expected": {"Privacy Compliance Report", "Regulatory Audit Report"},
                "limit": 3,
            },
            {
                "query": "What will our expenses look like next quarter?",
                "expected": {"Expense Forecast"},
                "limit": 2,
            },
            {
                "query": "Planned versus actual production",
                "expected": {
                    "Production Planning Forecast",
                    "Production Variance Report",
                },
                "limit": 3,
            },
            {
                "query": "inventory levels by warehouse",
                "expected": {"Inventory Status"},
                "limit": 2,
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
        limit: int = 6,
    ) -> tuple[float, float]:
        """
        We use the precision@k and recall@k metrics to evaluate our search implementation
        (reference: https://www.evidentlyai.com/ranking-metrics/precision-recall-at-k).
        These are metrics suited for recommender problems, which transfer to search.
        (Metrics used for classification problems are not well suited for search f.e.)
        """
        start_time = time.perf_counter()
        response = client.get(
            "/api/v2/search/output_ports",
            params={"query": query, "limit": limit},
        )
        end_time = time.perf_counter()

        assert response.status_code == 200, response.text
        assert end_time - start_time < latency_bound, (
            f"Output Port search took longer than {latency_bound * 1000} ms"
        )

        output = GetDataProductOutputPortsResponse.model_validate(response.json())
        assert len(output.output_ports) <= limit, "Query limit exceeded"

        positives = {port.name for port in output.output_ports}
        matches = len(expected.intersection(positives))

        precision_at_k = matches / len(output.output_ports)
        recall_at_k = matches / len(expected)

        assert precision_at_k >= precision_bound, (
            f"Precision score too low for query '{query}' ({precision_at_k} < {precision_bound})"
        )
        assert recall_at_k >= recall_bound, (
            f"Recall score too low for query '{query}' ({recall_at_k} < {recall_bound})"
        )
        return precision_at_k, recall_at_k

    @staticmethod
    def setup(session) -> tuple[Dataset, Dataset, Dataset]:
        RoleService(db=session).initialize_prototype_roles()
        ds_1 = DatasetFactory(name="Customer Data")
        ds_2 = DatasetFactory(name="Sales Data")
        ds_3 = DatasetFactory(name="Internal Metrics")
        OutputPortService(db=session).recalculate_search_for_all_output_ports()
        return ds_1, ds_2, ds_3

    @staticmethod
    def reseed(session) -> None:
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
        OutputPortService(db=session).recalculate_search_for_all_output_ports()
        end_time = time.perf_counter()
        assert (duration := end_time - start_time) <= EMBEDDING_LATENCY_BOUND, (
            f"Embeddings take too long to calculate ({duration} > {EMBEDDING_LATENCY_BOUND})"
        )
