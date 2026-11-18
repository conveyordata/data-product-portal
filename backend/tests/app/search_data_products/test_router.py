import os
import time
from typing import Final

import pytest
from alembic import command

from app.authorization.role_assignments.enums import AssignmentFilter
from app.authorization.roles.schema import Scope
from app.data_products.model import DataProduct, DataProductVisibility
from app.data_products.service import DataProductService
from app.database.database import engine
from app.db_tool import seed_cmd
from app.plugins.migrations import (
    _config,
    _version_locations,
    migrate_all,
    owns_a_table,
)
from app.plugins.registry import plugin_registry
from app.search_data_products.schema_response import SearchDataProductsResponse
from app.settings import settings
from tests import engine as test_engine
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

ENDPOINT = "/api/v2/search/data_products"
# A Data Product embeds the text of its Output Ports and Technical Assets as well
EMBEDDING_LATENCY_BOUND: Final[float] = 2 * float(
    os.getenv("TEST_EMBEDDING_LATENCY_BOUND", 1.100)
)  # seconds
LATENCY_BOUND: Final[float] = float(os.getenv("TEST_LATENCY_BOUND", 0.300))  # seconds
PRECISION_BOUND: Final[float] = 0.5
RECALL_BOUND: Final[float] = 0.8


class TestDataProductSearchRouter:
    def test_search_data_products__ranks_matches_first(self, session, client):
        churn, _, _ = self.setup(session)

        response = client.get(ENDPOINT, params={"query": "customer churn"})

        assert response.status_code == 200, response.text
        assert response.json()["data_products"][0]["id"] == str(churn.id)

    def test_search_data_products__no_query_sorts_by_name(self, session, client):
        data_products = self.setup(session)

        response = client.get(ENDPOINT)

        assert response.status_code == 200, response.text
        assert [dp["name"] for dp in response.json()["data_products"]] == sorted(
            dp.name for dp in data_products
        )

    def test_search_data_products__limit(self, session, client):
        self.setup(session)

        response = client.get(ENDPOINT, params={"query": "data", "limit": 2})

        assert response.status_code == 200, response.text
        assert len(response.json()["data_products"]) == 2

    def test_search_data_products__query_too_short(self, client):
        response = client.get(ENDPOINT, params={"query": "ab"})

        assert response.status_code == 422, response.text

    def test_search_data_products__only_assigned(self, session, client):
        churn, _, _ = self.setup(session)
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        DataProductRoleAssignmentFactory(
            data_product_id=churn.id,
            role_id=RoleFactory(scope=Scope.DATA_PRODUCT, permissions=[]).id,
            identity_id=user.id,
        )

        response = client.get(
            ENDPOINT,
            params={
                "query": "sales",
                "assignment_filter": AssignmentFilter.ONLY_ASSIGNED.value,
            },
        )

        assert response.status_code == 200, response.text
        assert [dp["id"] for dp in response.json()["data_products"]] == [str(churn.id)]

    def test_search_data_products__excludes_hidden(self, session, client):
        UserFactory(external_id=settings.DEFAULT_USERNAME)
        hidden = DataProductFactory(
            name="Hidden Churn", visibility=DataProductVisibility.HIDDEN
        )
        DataProductService(session).recalculate_search_for_all_data_products()

        response = client.get(ENDPOINT, params={"query": "churn"})

        assert response.status_code == 200, response.text
        assert str(hidden.id) not in {
            dp["id"] for dp in response.json()["data_products"]
        }

    @pytest.mark.commits
    def test_benchmark_data_products(self, session, client):
        self.reseed(session)

        configuration = [
            {
                "query": "Which customers are we at risk of losing?",
                "expected": {"Customer Churn Prediction", "Customer Lifetime Value"},
                "limit": 3,
            },
            {
                "query": "Which campaigns delivered the best ROI?",
                "expected": {"Marketing Campaign Analysis"},
                "limit": 2,
            },
            {
                "query": "Which features are used the most?",
                "expected": {
                    "Feature Usage Metrics",
                    "Product Performance Dashboard",
                    "Release Impact Analysis",
                    "User Feedback Analysis",
                },
                "limit": 5,
            },
            {
                "query": "Are we GDPR compliant?",
                "expected": {"Data Privacy Compliance", "Regulatory Audit Tracker"},
                "limit": 4,
            },
            {
                "query": "What will our expenses look like next quarter?",
                "expected": {"Expense Forecasting"},
                "limit": 2,
            },
            {
                "query": "Planned versus actual production",
                "expected": {"Production Planning Insights"},
                "limit": 2,
            },
            {
                "query": "inventory levels by warehouse",
                "expected": {
                    "Inventory Management",
                    "Warehouse Automation Metrics",
                },
                "limit": 3,
            },
        ]

        valid_data_products = {
            dp.name
            for dp in DataProductService(session).get_data_products(
                assignment_filter=AssignmentFilter.ALL
            )
        }
        for config in configuration:
            for value in config["expected"]:
                assert value in valid_data_products, (
                    f"{value} is not registered as the name of a Data Product"
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
            f"Average recall score too low ({avg_recall} < {RECALL_BOUND})"
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
        response = client.get(ENDPOINT, params={"query": query, "limit": limit})
        end_time = time.perf_counter()

        assert response.status_code == 200, response.text
        assert end_time - start_time < latency_bound, (
            f"Data Product search took longer than {latency_bound * 1000} ms"
        )

        output = SearchDataProductsResponse.model_validate(response.json())
        assert len(output.data_products) <= limit, "Query limit exceeded"

        positives = {dp.name for dp in output.data_products}
        matches = len(expected.intersection(positives))

        precision_at_k = matches / len(output.data_products)
        recall_at_k = matches / len(expected)

        assert precision_at_k >= precision_bound, (
            f"Precision score too low for query '{query}' ({precision_at_k} < {precision_bound})"
        )
        assert recall_at_k >= recall_bound, (
            f"Recall score too low for query '{query}' ({recall_at_k} < {recall_bound})"
        )
        return precision_at_k, recall_at_k

    @staticmethod
    def setup(session) -> tuple[DataProduct, DataProduct, DataProduct]:
        churn = DataProductFactory(
            name="Customer Churn Data", description="Predicts which customers leave"
        )
        sales = DataProductFactory(
            name="Sales Data", description="Revenue per sales region"
        )
        metrics = DataProductFactory(
            name="Internal Metrics", description="Platform health indicators"
        )
        DataProductService(session).recalculate_search_for_all_data_products()
        return churn, sales, metrics

    @staticmethod
    def reseed(session) -> None:
        # A bare alembic.ini Config only knows core's own versions folder, but
        # the shared version table also holds every plugin's tracked revision
        # by this point in the suite - build the same all-branches config
        # migrate_all does. Several of core's own migrations `depends_on` a
        # plugin's baseline (see migrations.py), and Alembic enforces that
        # ordering on the way down too, so a single downgrade to "base" is
        # safe: dependents (core) always go before their dependency (the
        # plugin), which is also the order a plugin's table can actually be
        # dropped in, since core's data still references it until then.
        url = engine.url.render_as_string(hide_password=False)
        owning_plugins = [p for p in plugin_registry.discovered() if owns_a_table(p)]
        cfg = _config(_version_locations(owning_plugins), url)
        command.downgrade(cfg, "base")

        migrate_all(owning_plugins, engine)
        # Pooled connections hold prepared statements bound to the dropped types.
        engine.dispose()
        test_engine.dispose()

        seed_cmd(path="./sample_data.sql")

        start_time = time.perf_counter()
        DataProductService(db=session).recalculate_search_for_all_data_products()
        end_time = time.perf_counter()
        assert (duration := end_time - start_time) <= EMBEDDING_LATENCY_BOUND, (
            f"Embeddings take too long to calculate ({duration} > {EMBEDDING_LATENCY_BOUND})"
        )
