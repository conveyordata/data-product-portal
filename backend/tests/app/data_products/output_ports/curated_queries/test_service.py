from app.data_products.output_ports.curated_queries.schema_request import (
    OutputPortCuratedQueryInput,
)
from app.data_products.output_ports.curated_queries.service import (
    DatasetCuratedQueryService,
)
from tests.factories import DatasetFactory


class TestCuratedQueriesService:
    def test_replace_curated_queries_orders_results(self, session):
        dataset = DatasetFactory()
        service = DatasetCuratedQueryService(session)

        curated_queries = [
            OutputPortCuratedQueryInput(
                title="First query",
                description=None,
                query_text="SELECT 1",
            ),
            OutputPortCuratedQueryInput(
                title="Second query",
                description="Focus on highest priority",
                query_text="SELECT 2",
            ),
            OutputPortCuratedQueryInput(
                title="Third query",
                description=None,
                query_text="SELECT 3",
            ),
        ]

        result = service.replace_curated_queries(dataset.id, curated_queries)
        assert [item.title for item in result.output_port_curated_queries] == [
            "First query",
            "Second query",
            "Third query",
        ]

    def test_replace_curated_queries_clears_existing(self, session):
        dataset = DatasetFactory()
        service = DatasetCuratedQueryService(session)

        service.replace_curated_queries(
            dataset.id,
            [
                OutputPortCuratedQueryInput(
                    title="Keep me",
                    description=None,
                    query_text="SELECT 1",
                )
            ],
        )

        result_after_clear = service.replace_curated_queries(dataset.id, [])
        assert result_after_clear.output_port_curated_queries == []
